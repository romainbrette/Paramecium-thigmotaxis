%  compute_velocity_field
%
%  f1L:   The body forces, in the lab frame
%  f2L:   The traction layer forces, in the lab frame
%  Cdata: Cell face colors

function [f1L,f2L,Cdata] = compute_velocity_field(X1L,X2L,tri,og_flag,f2L,params);

  % ----- Solves for the forces on the body points -----

  % Fluid parameters
  mu  = params.mu;
  eps = params.eps;
  plane_vec = [0;0;1;0];

  % Regularized Stokeslet matrices
  M11 = form_stokes_image_system_3D_cm_fast(X1L,X1L,eps,mu,plane_vec);
  M12 = form_stokes_image_system_3D_cm_fast(X1L,X2L,eps,mu,plane_vec);

  % Force solve, reshape
  f1L = M11 \ (-M12*f2L);
  f1L = reshape(f1L, [], 3);
  f2L = reshape(f2L, [], 3);

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

  % Generate Cartesian grid with equal spacing
  x = x_min + (0:Nx-1)*ds;
  y = y_min + (0:Ny-1)*ds;

  % ----- Determine oral-groove face colors -----
  og_count = ...
      og_flag(tri(:,1)) + ...
      og_flag(tri(:,2)) + ...
      og_flag(tri(:,3));

  % Initialize face color data
  Nfaces = size(tri,1);
  Cdata = zeros(Nfaces,3);

  % 3 groove vertices: medium blue
  Cdata(og_count == 3,:) = repmat( ...
      [0.10 0.35 0.70], ...
      sum(og_count == 3),1);

  % 2 groove vertices: lighter blue
  Cdata(og_count == 2,:) = repmat( ...
      [0.25 0.50 0.80], ...
      sum(og_count == 2),1);

  % 1 groove vertex: light sky blue
  Cdata(og_count == 1,:) = repmat( ...
      [0.50 0.70 0.90], ...
      sum(og_count == 1),1);

  % 0 groove vertices: gray
  Cdata(og_count == 0,:) = repmat( ...
      [0.60 0.60 0.60], ...
      sum(og_count == 0),1);

  % ----- Export visualization data -----

  if params.export_data

      % Generate 2D velocity grid at specified height
      z_slice = params.z_slice;

      [grid2d.x,grid2d.y] = meshgrid(x,y);

      grid2d.z = z_slice*ones(size(grid2d.x));

      X_grid_export = [ ...
          grid2d.x(:), ...
          grid2d.y(:), ...
          grid2d.z(:)];

      for k=1:length(grid2d.x(:))
         %fprintf('computing veloicty pt %i of %i \n',k,length(grid2d.x(:)));

         Mx1_export = form_stokes_image_system_3D_cm_fast( ...
             X_grid_export(k,:),X1L,eps,mu,plane_vec);

         Mx2_export = form_stokes_image_system_3D_cm_fast( ...
             X_grid_export(k,:),X2L,eps,mu,plane_vec);

         % Compute velocity on the export grid
         u_export(k,:) = Mx1_export*f1L(:) + Mx2_export*f2L(:);
      end
         u_export = u_export(:);

      % Store velocity field
      flow_export.U  = reshape(u_export,[],3);
      flow_export.Ux = reshape( ...
          flow_export.U(:,1), ...
          size(grid2d.x));

      flow_export.Uy = reshape( ...
          flow_export.U(:,2), ...
          size(grid2d.y));

      flow_export.Uz = reshape( ...
          flow_export.U(:,3), ...
          size(grid2d.z));

      X = grid2d.x';
      Y = grid2d.y';
      U = flow_export.Ux';
      V = flow_export.Uy';

      % Flatten into [x, y, u, v]
      out = [X(:),Y(:),U(:),V(:)];

      % Export 2D velocity field
      dlmwrite( ...
          fullfile(params.output_dir,'vel_2D.txt'), ...
          out, ...
          'delimiter',' ', ...
          'precision','%.8f');

      fprintf( ...
          'Exported velocity field at z = %.4f\n', ...
          z_slice);

      % Export cell vertices
      dlmwrite( ...
          fullfile(params.output_dir,'cell_vertices.txt'), ...
          X1L, ...
          'delimiter',' ', ...
          'precision','%.8f');

      fprintf('Exported cell vertices\n');

      % Export traction-layer vertices
      dlmwrite( ...
          fullfile(params.output_dir,'cell_traction_vertices.txt'), ...
          X2L, ...
          'delimiter',' ', ...
          'precision','%.8f');

      fprintf('Exported traction-layer vertices\n');

      % Export z-slice height
      dlmwrite( ...
          fullfile(params.output_dir,'z_slice.txt'), ...
          z_slice, ...
          'delimiter',' ', ...
          'precision','%.8f');

      fprintf('Exported z-slice height\n');

      % Export cell triangulation
      dlmwrite( ...
          fullfile(params.output_dir,'cell_triangles.txt'), ...
          tri, ...
          'delimiter',' ', ...
          'precision','%d');

      fprintf('Exported cell triangulation\n');

      % Export face colors
      dlmwrite( ...
          fullfile(params.output_dir,'cell_face_colors.txt'), ...
          Cdata, ...
          'delimiter',' ', ...
          'precision','%.6f');

      fprintf('Exported face colors\n');
  end
end
