%  build_cell_geometry
%
%  X1:         The body points, in the body frame
%  X2:         The traction layer points, in the body frame
%  tri:        The surface triangulation to be used in plotting
%  f2:         The traction forces on the traction layer, in the body frame
%  og_flag:    The boolean array that identifies points in the oral groove

function [X1,X2,tri,f2,og_flag] = build_cell_geometry(Ns,params);

  % ----- Interpolate rho(z) from Paramecium outline -----

  % Read in the rho vs z outline data
  outline = load(fullfile(params.input_dir,'Paramecium_outline.txt'));
  z_outline   = outline(:,2);
  rho_outline = outline(:,1);

  % Interpolate rho vs z
  rho_z_interp = pchip(z_outline,rho_outline);
  rho_z_fun = @(z) ppval(rho_z_interp,z);

  % ----- Loads spheroidal mesh / triangulation, computes coordinates -----

  % Loads the corresponding point and triangulation sets
  X_spheroid = load(fullfile(params.meshdir,sprintf('dm_spheroid_%i_points.txt',Ns)));
  tri = load(fullfile(params.meshdir,sprintf('dm_spheroid_%i_tris.txt',Ns)));

  % Evaluates the values of rho for all body points values from the spheroid mesh
  rho = ppval(rho_z_interp,X_spheroid(:,3));

  % Compute the angular coordinates for all body points
  theta = atan2(rho,X_spheroid(:,3));
  phi   = atan2(X_spheroid(:,2), X_spheroid(:,1));

  % ----- Interpolate rho(th), z(th), and theta(z) from mesh points -----

  % Interpolated functions are needed to calculate surface vectors
  % Mesh points aren't stored in any particular order
  % Array structures are needed to sort theta, rho, and  z values for interpolation

  th_rho = zeros(Ns+2,2);
  th_rho(2:Ns+1,1) = theta;
  th_rho(2:Ns+1,2) = rho;
  th_rho(1,:) = [0,0]; % Add in boundary values at theta = 0
  th_rho(Ns+2,:) = [pi,0]; % Add in boundary values at theta = pi

  th_z = zeros(Ns+2,2);
  th_z(2:Ns+1,1) = theta;
  th_z(2:Ns+1,2) = X_spheroid(:,3);
  th_z(1,:) = [0,1];
  th_z(Ns+2,:) = [pi,-1];

  z_th = zeros(Ns+2,2);
  z_th(2:Ns+1,1) = X_spheroid(:,3);
  z_th(2:Ns+1,2) = theta;
  z_th(1,:) = [-1,pi];
  z_th(Ns+2,:) = [1,1e-12]; % Small epsilon stored here not 0 to prevent bugs

  % We must sort by increasing theta, and have one body point per input
  th_rho = sortrows(th_rho,[1]);
  [~,I] = unique(th_rho(:,1));
  th_rho_unique = zeros(length(I),2);
  th_rho_unique = th_rho(I,:);

  th_z = sortrows(th_z,[1]);
  [~,I] = unique(th_z(:,1));
  th_z_unique = zeros(length(I),2);
  th_z_unique = th_z(I,:);

  z_th = sortrows(z_th,[1]);
  [~,I] = unique(z_th(:,1));
  z_th_unique = zeros(length(I),2);
  z_th_unique = z_th(I,:);

  % Interpolated rho(theta), z(theta), theta(z) functions
  rho_th_interp = pchip(th_rho_unique(:,1),th_rho_unique(:,2));
  z_th_interp   = pchip(th_z_unique(:,1),th_z_unique(:,2));
  th_z_interp   = pchip(z_th_unique(:,1),z_th_unique(:,2));

  rho_th_fun = @(th) ppval(rho_th_interp,th);
  z_th_fun = @(th) ppval(z_th_interp,th);
  th_z_fun = @(z) ppval(th_z_interp,z);

  % ----- Compute body points via the parametrization X(theta,phi) -----
  X1 = zeros(Ns,3);
  X1(:,1) = rho_th_fun(theta).*cos(phi);
  X1(:,2) = rho_th_fun(theta).*sin(phi);
  X1(:,3) = z_th_fun(theta);

  % ----- Oral groove functions and parameters -----

  % Read in the oral groove width(z) outline data
  outline = load(fullfile(params.input_dir,'Oral_groove_width_outline.txt'));
  zg_outline = outline(:,1);
  w_outline  = outline(:,2); % This is the 1/2 width of the oral groove
  w_sf = 1.0; % A scale factor to widen / shrink the oral groove width
  w_outline  = 2.*w_sf.*w_outline; % Now full-width

  % Oral groove parameters
  phi_0 = 25*pi/180; % Controls the initial angling of the oral groove curve
  th_min = 3*pi/180; % The minimum theta value where the oral groove begins
  z_min = min(zg_outline); % The domain of this width function extends below mouth
  th_max = th_z_fun(z_min); % The corresponding theta to this z_min

  % Interpolated w(theta) function
  w_th_interp = pchip(th_z_fun(zg_outline),w_outline);
  w_th_fun = @(th) ppval(w_th_interp,th);

  % Oral groove centerline curve
  gamma_fun = @(th) phi_0.*cos(th);

  % Boolean variable to flag all points inside the oral groove
  og_flag = false(Ns,1);
  % Loop over all mesh points, flag the oral groove points
  for i=1:Ns
    if theta(i) > th_min && theta(i) < th_max % Polar range for oral groove
      phi_g = gamma_fun(theta(i)); % phi angle on the oral groove

      % Point on groove curve at the given point's polar angle
      xg = rho_th_fun(theta(i))*cos(phi_g);
      yg = rho_th_fun(theta(i))*sin(phi_g);
      zg = z_th_fun(theta(i));

      % Distance from mesh point to oral groove point
      dist = norm(X1(i,:) - [xg, yg, zg]);

      % Flag with width-dependent threshold
      if dist < w_th_fun(theta(i))/2
          og_flag(i) = true;
      end
    end
  end

  % ----- Compute orthonormal surface vectors -----

  theta_hat = zeros(Ns,3);
  phi_hat = zeros(Ns,3);
  n_hat = zeros(Ns,3);

  % Numerically differentiate rho_th & z_th with respect to theta
  h = 1e-5;
  drho_dth = (rho_th_fun(theta+h) ...
             -rho_th_fun(theta-h))./(2*h);

  dz_dth    = (z_th_fun(theta+h) ...
             -z_th_fun(theta-h))./(2*h);

  % Orthonormal surface vectors
  theta_hat = zeros(Ns,3);
  phi_hat   = zeros(Ns,3);
  n_hat     = zeros(Ns,3);

  theta_hat(:,1) = drho_dth.*cos(phi);
  theta_hat(:,2) = drho_dth.*sin(phi);
  theta_hat(:,3) = dz_dth;

  phi_hat(:,1) = -rho.*sin(phi);
  phi_hat(:,2) =  rho.*cos(phi);
  % phi_hat(:,3) is already 0

  % Outward unit normal = theta_hat x phi_hat
  n_hat = cross(theta_hat,phi_hat,2);

  % Normalize
  theta_hat = theta_hat ./ (vecnorm(theta_hat,2,2)+1e-12);
  phi_hat = phi_hat ./ (vecnorm(phi_hat,2,2)+1e-12);
  n_hat = n_hat ./ (vecnorm(n_hat,2,2)+1e-12);

    % Normalize
  theta_hat = theta_hat ./ (vecnorm(theta_hat,2,2)+1e-12);
  phi_hat = phi_hat ./ (vecnorm(phi_hat,2,2)+1e-12);
  n_hat = n_hat ./ (vecnorm(n_hat,2,2)+1e-12);

  % ----- Correct surface normals at the poles -----

  % The azimuthal direction is undefined where rho = 0.
  % At the anterior and posterior poles, the outward normal
  % must instead point directly along the long (z) axis.

  pole_tol = 1e-6;

  posterior_idx = rho < pole_tol & X1(:,3) < 0;
  anterior_idx  = rho < pole_tol & X1(:,3) > 0;

  n_hat(posterior_idx,:) = repmat( ...
      [0,0,-1], ...
      sum(posterior_idx),1);

  n_hat(anterior_idx,:) = repmat( ...
      [0,0,1], ...
      sum(anterior_idx),1);

  % ----- Compute oral groove tangent vectors -----

  T_hat = zeros(Ns,3);
  groove_idx = find(og_flag);
  th_g = theta(groove_idx);
  phi_g = gamma_fun(th_g);

  T_hat(groove_idx,1) = drho_dth(groove_idx).*cos(phi_g)-rho(groove_idx).*sin(phi_g).*(-phi_0*sin(th_g));
  T_hat(groove_idx,2) = drho_dth(groove_idx).*sin(phi_g)+rho(groove_idx).*cos(phi_g).*(-phi_0*sin(th_g));
  T_hat(groove_idx,3) = dz_dth(groove_idx);

  % Normalize
  T_hat(og_flag,:) = T_hat(og_flag,:)./vecnorm(T_hat(og_flag,:),2,2);

  % ----- Compute traction layer points and quadratures -----

  % Computes outer traction layer with outward normal projection
  eps_trac = params.eps_trac;
  X2 = X1 + eps_trac.*n_hat;

  % Quadrature weights on the traction layer
  dA = quadweights(X2,tri);

  % ----- Prescribe traction layer forces -----

  % Traction layer force magnitudes for locomotor and oral groove cilia
  F_mag = zeros(Ns,1);
  F_mag(og_flag)  = params.F_groove;
  F_mag(~og_flag) = params.F_body;

  % Angle of locomotor ciliary traction force
  alpha = params.alpha;

  % Prescribe forces at each traction layer point
  f2 = zeros(Ns,3);

  % Forces in oral groove are tangent to oral groove curve
  f2(og_flag,:) = F_mag(og_flag).*T_hat(og_flag,:);

  % Forces in locomotor cilia are angled relative to theta_hat by alpha
  f2(~og_flag,:) = F_mag(~og_flag).*(cos(alpha).*theta_hat(~og_flag,:)...
                                          +sin(alpha).*phi_hat(~og_flag,:));

  % Scales the traction forces by the area of each point
  f2 = dA.*f2;
end
