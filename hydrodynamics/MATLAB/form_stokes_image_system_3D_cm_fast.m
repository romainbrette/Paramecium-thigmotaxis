function M = form_stokes_image_system_3D_cm_fast(X, X0, epsilon, mu, plane_vec)
% Fast Regularized Stokeslets Method of Images Matrix
% Computes components separately to prevent memory overload 

Nt = size(X, 1);
Ns = size(X0, 1);

% Normalize plane so that n has unit length
n = plane_vec(1:3);
d = plane_vec(4) / norm(n);
n = n / norm(n);

% Reflection operator (3x3)
P_mat = eye(3) - 2 * (n * n');

% Stokeslet 
% displacement vectors (Nt x Ns)
Xhat = X(:,1) - X0(:,1)';
Yhat = X(:,2) - X0(:,2)';
Zhat = X(:,3) - X0(:,3)';

XX = Xhat.^2;   YY = Yhat.^2;   ZZ = Zhat.^2;
XY = Xhat.*Yhat; XZ = Xhat.*Zhat; YZ = Yhat.*Zhat;

r2 = XX + YY + ZZ;
re2 = r2 + epsilon^2;
re = sqrt(re2);

H2 = 1.0 ./ (re2 .* re); % 1/re^3
H1 = (r2 + 2*epsilon^2) .* H2;

const_s = 1 / (8 * pi * mu);
S11 = (H1 + H2.*XX) .* const_s;  S12 = (H2.*XY) .* const_s;       S13 = (H2.*XZ) .* const_s;
S21 = S12;                       S22 = (H1 + H2.*YY) .* const_s;  S23 = (H2.*YZ) .* const_s;
S31 = S13;                       S32 = S23;                       S33 = (H1 + H2.*ZZ) .* const_s;

% Image Stokeslet 
% Distance to plane for each source point
h_vec = X0 * n - d; 
h = abs(h_vec); 

% Reflect source points across the plane
X0_im = X0 - 2 * h_vec * n';

% Recompute displacements for image points
Xhat_im = X(:,1) - X0_im(:,1)';
Yhat_im = X(:,2) - X0_im(:,2)';
Zhat_im = X(:,3) - X0_im(:,3)';

XX_im = Xhat_im.^2;   YY_im = Yhat_im.^2;   ZZ_im = Zhat_im.^2;
XY_im = Xhat_im.*Yhat_im; XZ_im = Xhat_im.*Zhat_im; YZ_im = Yhat_im.*Zhat_im;

r2_im = XX_im + YY_im + ZZ_im;
re2_im = r2_im + epsilon^2;
re_im = sqrt(re2_im);

H2_im = 1.0 ./ (re2_im .* re_im);
H1_im = (r2_im + 2*epsilon^2) .* H2_im;

const_im = -1 / (8 * pi * mu);
IM11 = (H1_im + H2_im.*XX_im) .* const_im; IM12 = (H2_im.*XY_im) .* const_im;       IM13 = (H2_im.*XZ_im) .* const_im;
IM21 = IM12;                               IM22 = (H1_im + H2_im.*YY_im) .* const_im; IM23 = (H2_im.*YZ_im) .* const_im;
IM31 = IM13;                               IM32 = IM23;                               IM33 = (H1_im + H2_im.*ZZ_im) .* const_im;

% Potential Dipole 
re5_inv = 1.0 ./ (re2_im.^2 .* re_im); % 1/re^5
D2_im = -3 * re5_inv;
D1_im = (r2_im - 2*epsilon^2) .* re5_inv;

% Unscaled PD Blocks
M11 = D1_im + D2_im.*XX_im; M12 = D2_im.*XY_im;       M13 = D2_im.*XZ_im;
M21 = M12;                  M22 = D1_im + D2_im.*YY_im; M23 = D2_im.*YZ_im;
M31 = M13;                  M32 = M23;                  M33 = D1_im + D2_im.*ZZ_im;

scale_pd = (h.^2)' / (4 * pi * mu); % 1 x Ns for implicit column scaling

% Right multiply by P_mat and scale
PD11 = (M11*P_mat(1,1) + M12*P_mat(2,1) + M13*P_mat(3,1)) .* scale_pd;
PD12 = (M11*P_mat(1,2) + M12*P_mat(2,2) + M13*P_mat(3,2)) .* scale_pd;
PD13 = (M11*P_mat(1,3) + M12*P_mat(2,3) + M13*P_mat(3,3)) .* scale_pd;
PD21 = (M21*P_mat(1,1) + M22*P_mat(2,1) + M23*P_mat(3,1)) .* scale_pd;
PD22 = (M21*P_mat(1,2) + M22*P_mat(2,2) + M23*P_mat(3,2)) .* scale_pd;
PD23 = (M21*P_mat(1,3) + M22*P_mat(2,3) + M23*P_mat(3,3)) .* scale_pd;
PD31 = (M31*P_mat(1,1) + M32*P_mat(2,1) + M33*P_mat(3,1)) .* scale_pd;
PD32 = (M31*P_mat(1,2) + M32*P_mat(2,2) + M33*P_mat(3,2)) .* scale_pd;
PD33 = (M31*P_mat(1,3) + M32*P_mat(2,3) + M33*P_mat(3,3)) .* scale_pd;

% Stokeslet Doublet 
H3_im = -(r2_im + 4*epsilon^2) .* re5_inv;
H4_im = D2_im;

XdotN = Xhat_im.*n(1) + Yhat_im.*n(2) + Zhat_im.*n(3);
D_sd = H2_im .* XdotN; % Diagonal component

% Unscaled SD Components
SD1_11 = H2_im.*Xhat_im.*n(1); SD1_12 = H2_im.*Xhat_im.*n(2); SD1_13 = H2_im.*Xhat_im.*n(3);
SD1_21 = H2_im.*Yhat_im.*n(1); SD1_22 = H2_im.*Yhat_im.*n(2); SD1_23 = H2_im.*Yhat_im.*n(3);
SD1_31 = H2_im.*Zhat_im.*n(1); SD1_32 = H2_im.*Zhat_im.*n(2); SD1_33 = H2_im.*Zhat_im.*n(3);

SD3_11 = H3_im.*Xhat_im.*n(1); SD3_12 = H3_im.*Yhat_im.*n(1); SD3_13 = H3_im.*Zhat_im.*n(1);
SD3_21 = H3_im.*Xhat_im.*n(2); SD3_22 = H3_im.*Yhat_im.*n(2); SD3_23 = H3_im.*Zhat_im.*n(2);
SD3_31 = H3_im.*Xhat_im.*n(3); SD3_32 = H3_im.*Yhat_im.*n(3); SD3_33 = H3_im.*Zhat_im.*n(3);

SD4_11 = H4_im.*XdotN.*XX_im; SD4_12 = H4_im.*XdotN.*XY_im; SD4_13 = H4_im.*XdotN.*XZ_im;
SD4_21 = H4_im.*XdotN.*XY_im; SD4_22 = H4_im.*XdotN.*YY_im; SD4_23 = H4_im.*XdotN.*YZ_im;
SD4_31 = H4_im.*XdotN.*XZ_im; SD4_32 = H4_im.*XdotN.*YZ_im; SD4_33 = H4_im.*XdotN.*ZZ_im;

% Sum unscaled blocks (adding D_sd to the diagonals)
U_SD11 = SD1_11 + D_sd + SD3_11 + SD4_11; U_SD12 = SD1_12 + SD3_12 + SD4_12;        U_SD13 = SD1_13 + SD3_13 + SD4_13;
U_SD21 = SD1_21 + SD3_21 + SD4_21;        U_SD22 = SD1_22 + D_sd + SD3_22 + SD4_22; U_SD23 = SD1_23 + SD3_23 + SD4_23;
U_SD31 = SD1_31 + SD3_31 + SD4_31;        U_SD32 = SD1_32 + SD3_32 + SD4_32;        U_SD33 = SD1_33 + D_sd + SD3_33 + SD4_33;

scale_sd = (-2 * h') / (8 * pi * mu);

% Right multiply by P_mat and scale
SD11 = (U_SD11*P_mat(1,1) + U_SD12*P_mat(2,1) + U_SD13*P_mat(3,1)) .* scale_sd;
SD12 = (U_SD11*P_mat(1,2) + U_SD12*P_mat(2,2) + U_SD13*P_mat(3,2)) .* scale_sd;
SD13 = (U_SD11*P_mat(1,3) + U_SD12*P_mat(2,3) + U_SD13*P_mat(3,3)) .* scale_sd;
SD21 = (U_SD21*P_mat(1,1) + U_SD22*P_mat(2,1) + U_SD23*P_mat(3,1)) .* scale_sd;
SD22 = (U_SD21*P_mat(1,2) + U_SD22*P_mat(2,2) + U_SD23*P_mat(3,2)) .* scale_sd;
SD23 = (U_SD21*P_mat(1,3) + U_SD22*P_mat(2,3) + U_SD23*P_mat(3,3)) .* scale_sd;
SD31 = (U_SD31*P_mat(1,1) + U_SD32*P_mat(2,1) + U_SD33*P_mat(3,1)) .* scale_sd;
SD32 = (U_SD31*P_mat(1,2) + U_SD32*P_mat(2,2) + U_SD33*P_mat(3,2)) .* scale_sd;
SD33 = (U_SD31*P_mat(1,3) + U_SD32*P_mat(2,3) + U_SD33*P_mat(3,3)) .* scale_sd;

% Rotlet
H5_im = H3_im + H2_im;
R_D = -H5_im .* XdotN; % Diagonal component

R11 = H5_im.*Xhat_im.*n(1); R12 = H5_im.*Yhat_im.*n(1); R13 = H5_im.*Zhat_im.*n(1);
R21 = H5_im.*Xhat_im.*n(2); R22 = H5_im.*Yhat_im.*n(2); R23 = H5_im.*Zhat_im.*n(2);
R31 = H5_im.*Xhat_im.*n(3); R32 = H5_im.*Yhat_im.*n(3); R33 = H5_im.*Zhat_im.*n(3);

scale_rot = (2 * h') / (8 * pi * mu);

ROT11 = (R11 + R_D) .* scale_rot; ROT12 = R12 .* scale_rot;         ROT13 = R13 .* scale_rot;
ROT21 = R21 .* scale_rot;         ROT22 = (R22 + R_D) .* scale_rot; ROT23 = R23 .* scale_rot;
ROT31 = R31 .* scale_rot;         ROT32 = R32 .* scale_rot;         ROT33 = (R33 + R_D) .* scale_rot;

% Final matrix assembly 
M = [S11 + IM11 + PD11 + SD11 + ROT11, S12 + IM12 + PD12 + SD12 + ROT12, S13 + IM13 + PD13 + SD13 + ROT13;
     S21 + IM21 + PD21 + SD21 + ROT21, S22 + IM22 + PD22 + SD22 + ROT22, S23 + IM23 + PD23 + SD23 + ROT23;
     S31 + IM31 + PD31 + SD31 + ROT31, S32 + IM32 + PD32 + SD32 + ROT32, S33 + IM33 + PD33 + SD33 + ROT33];

end