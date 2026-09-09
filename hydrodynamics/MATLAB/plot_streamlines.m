%  plot_streamlines

function plot_streamlines(X1L,X2L,tri,f1L,f2L,Cdata,params);

  % Fluid parameters
  mu  = params.mu;
  eps = params.eps;
  plane_vec = [0;0;1;0];

  % ----- Generates a 3D Cartesian grid surrounding the cell -----

  % Desired grid spacing
  %
  % grid_res is interpreted as the approximate number of grid
  % points across the cell's long axis.
  margin = 1;

  x_min = min(X1L(:,1)) - margin;
  x_max = max(X1L(:,1)) + margin;

  y_min = min(X1L(:,2)) - 1.5*margin;
  y_max = max(X1L(:,2)) + 1.5*margin;

  z_min = 1e-6;
  z_max = max(X1L(:,3)) + margin;

  % Compute a uniform grid spacing from the y-domain
  ds = (y_max - y_min) / (params.grid_res - 1);


  % Determine number of points required in each direction
  Nx = round((x_max - x_min)/ds) + 1;
  Ny = round((y_max - y_min)/ds) + 1;
  Nz = round((z_max - z_min)/ds) + 1;

  % Generate Cartesian grid with equal spacing
  x = x_min + (0:Nx-1)*ds;
  y = y_min + (0:Ny-1)*ds;
  z = z_min + (0:Nz-1)*ds;

  [grid3d.x,grid3d.y,grid3d.z] = meshgrid(x,y,z);

  X_grid = [ ...
      grid3d.x(:), ...
      grid3d.y(:), ...
      grid3d.z(:)];

  % ----- Compute velocity field on 3D grid -----

  for k=1:length(grid3d.x(:))
     %fprintf('computing veloicty pt %i of %i \n',k,length(grid3d.x(:)));

     Mx1 = form_stokes_image_system_3D_cm_fast( ...
         X_grid(k,:),X1L,eps,mu,plane_vec);

     Mx2 = form_stokes_image_system_3D_cm_fast( ...
         X_grid(k,:),X2L,eps,mu,plane_vec);

     u(k,:) = Mx1*f1L(:) + Mx2*f2L(:);
  end

  % Store velocity field
  flow.U  = reshape(u,[],3);
  flow.Ux = reshape(flow.U(:,1),size(grid3d.x));
  flow.Uy = reshape(flow.U(:,2),size(grid3d.y));
  flow.Uz = reshape(flow.U(:,3),size(grid3d.z));

  % ----- Generates a set of streamline seed points -----

  % Velocity field grid domain
  x_min = min(grid3d.x(:));
  x_max = max(grid3d.x(:));
  y_min = min(grid3d.y(:));
  y_max = max(grid3d.y(:));
  z_min = min(grid3d.z(:));
  z_max = max(grid3d.z(:));

  % Seeds occupy middle 50% of grid domain
  seed_frac = 0.5;

  x_mid = (x_min + x_max)/2;
  y_mid = (y_min + y_max)/2;
  x_half = seed_frac*(x_max-x_min)/2;
  y_half = seed_frac*(y_max-y_min)/2;

  seed_x_min = x_mid - x_half;
  seed_x_max = x_mid + x_half;
  seed_y_min = y_mid - y_half;
  seed_y_max = y_mid + y_half;

  % Generate seed points
  [sx,sy] = meshgrid( ...
    linspace(seed_x_min,seed_x_max,params.seed_res), ...
    linspace(seed_y_min,seed_y_max,params.seed_res));

  % Set seed heights between surface and traction layer
  sz = ones(size(sx))*(0.75)*min(X2L(:,3));

  % ----- Plot streamlines and cell -----
  figure(1);

%  % Plot xy-plane at z = 0
%  [xp,yp] = meshgrid( ...
%    linspace(x_min,x_max,20), ...
%    linspace(y_min,y_max,20));
%  zp = zeros(size(xp));
%
%  surf(xp,yp,zp, ...
%      'FaceColor',[0.85 0.85 0.85], ...
%      'EdgeColor','none', ...
%      'FaceAlpha',0.3);

  hold on

  % Plot streamlines in forward time
  h = streamline(grid3d.x,grid3d.y,grid3d.z,...
               flow.Ux,flow.Uy,flow.Uz,...
               sx,sy,sz);

  % Plot streamlines in backward time
  h = streamline(grid3d.x,grid3d.y,grid3d.z,...
               -flow.Ux,-flow.Uy,-flow.Uz,...
               sx,sy,sz);

  % Plot cell
  trisurf(tri,X1L(:,1),X1L(:,2),X1L(:,3), ...
          'FaceVertexCData',Cdata, ...
          'FaceColor','flat', ...
          'EdgeColor',[0.8 0.8 0.8], ...
          'FaceAlpha',0.9);

  % Format figure
  axis equal
  grid on
  xlabel('x')
  ylabel('y')
  zlabel('z')
  view([-127,9])
  camlight
  lighting gouraud
end
