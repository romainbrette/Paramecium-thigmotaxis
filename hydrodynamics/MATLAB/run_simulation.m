%  run_simulation.m - The main driver

clear;
close all;
clc;

% Project directories
matlab_dir = fileparts(mfilename('fullpath'));
project_dir = fileparts(matlab_dir);

input_dir = fullfile(matlab_dir,'inputs');
mesh_dir = fullfile(input_dir,'mesh_sets');
results_dir = fullfile(project_dir,'Results');

% Mesh sizes options
mesh_res = [304,710,1319,2514,5543];
res = 1; % Select mesh resolution
Ns = mesh_res(res);

% Parameters
params.mu        = 1; % Viscosity
params.eps       = 0.25*sqrt(4*pi/Ns); % Regularized Stokeslet parameter
params.eps_trac  = 10*2/120; % Width of the ciliary layer
params.alpha     = 30*pi/180; % Angle of locomotor cilia force
params.F_groove  = 1.00; % Strength of oral groove ciliary forcing
params.F_body    = 0.00; % Strength of locomotor ciliary forcing
params.phi_init  = 90*pi/180; % Roll angle when staging paramecium
params.beta_init = 5*pi/180; % Pitch angle
params.h         = 6*2/120; % Staging height above the surface
params.grid_res  = 25; % Grid density
params.seed_res  = 6; % Streamline seed density
params.z_slice   = 0.45; % Height of sliced velocity field for visualization
params.input_dir = input_dir; % Main input directory
params.meshdir   = mesh_dir; % Directory for the mesh data

% Create output directory
output_name = sprintf( ...
    'mesh_%d_force_ratio_%.2f_phi_%.0f', ...
    Ns, params.F_body, rad2deg(params.phi_init));

output_dir = fullfile(results_dir,output_name);

if ~exist(output_dir,'dir')
    mkdir(output_dir);
end

params.output_dir = output_dir;
params.export_data = true;

% Stores all body & traction layer points, surface vectors, traction forces, coordinates
[X1,X2,tri,f2,og_flag] = build_cell_geometry(Ns,params);

% Stages the swimmer above the surface
[X1L,X2L,f2L] = stage_swimmer(X1,X2,f2,params);

% Computes the 2D velocity field in a slice at specified z,
% writes the data to file
[f1L,f2L,Cdata] = compute_velocity_field(X1L,X2L,tri,og_flag,f2L,params);

% Plots Paramecium above the surface, along with streamlines
%plot_streamlines(X1L,X2L,tri,f1L,f2L,Cdata,params);

if params.export_data == true
  fprintf('\nSimulation complete.\n');
  fprintf('Results saved to:\n%s\n',output_dir);
else
  fprintf('\nSimulation complete.\n');
end
