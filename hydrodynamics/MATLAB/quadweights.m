%
% Given a set of points on the sphere compute quadrature weights
%
function dA = quadweights(X,tri);


% loop over each triangle
%  compute it's area
%  assign 1/3 of each area to each vertex
%
dA = zeros(length(X),1);
for k=1:length(tri)
  V1 = X(tri(k,1),:);
  V2 = X(tri(k,2),:);
  V3 = X(tri(k,3),:);

  A = 0.5*norm( cross(V2-V1,V3-V1) );
  dA(tri(k,1)) = dA(tri(k,1)) + A/3;
  dA(tri(k,2)) = dA(tri(k,2)) + A/3;
  dA(tri(k,3)) = dA(tri(k,3)) + A/3;

end
