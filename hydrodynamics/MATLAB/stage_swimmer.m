%  stage_swimmer
%
%  X1L:      The body points, in the lab frame
%  X2L:      The traction layer points, in the lab frame
%  f2L:      The traction layer forces, in the lab frame

function [X1L,X2L,f2L] = stage_swimmer(X1,X2,f2,params);

  % ----- Stages paramecium with a given pitch, roll, and height -----

  % Orientation posture parameters
  phi_init  = params.phi_init;
  phi_init  = phi_init + pi/2;
  beta_init = params.beta_init;
  beta_init = -(pi/2 + beta_init);
  h         = params.h;

  % Rotation matrices
  Rz = [cos(phi_init) -sin(phi_init) 0;
        sin(phi_init)  cos(phi_init) 0;
        0              0             1];

  Rx = [1 0 0;
        0 cos(beta_init) -sin(beta_init);
        0 sin(beta_init)  cos(beta_init)];

  % Rotate body and traction layer points to lab frame
  X1L = (Rx*Rz*X1')';
  X2L = (Rx*Rz*X2')';

  % Rotate forces to lab frame
  f2L = (Rx*Rz*f2')';
  f2L = f2L(:);

  % A translation vector that stages paramecium a given height above the surface
  X0 = [0 0 abs(min(X2L(:,3))) + h];

  % Translate body & traction layer points
  X1L = X1L + X0;
  X2L = X2L + X0;
end
