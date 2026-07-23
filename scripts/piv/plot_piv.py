'''
Plot PIV field

To add:
- save color bar
- normalize speed to fixed value
'''
import tkinter as tk
from tkinter import filedialog
import matplotlib
matplotlib.use('TkAgg')
from pylab import *

root = tk.Tk()
root.withdraw()  # Hide the main window
filename = filedialog.askopenfilename(initialdir=os.path.expanduser('~/Downloads/'), title='Choose a file')
folder = os.path.dirname(filename)

output_filename = os.path.join(folder, 'piv.pdf')

x, y, u, v = np.loadtxt(filename).T

# find grid
width = (diff(y)>0.).nonzero()[0][0]+1
height = len(x)//width
print(width, height)

x = x.reshape((height, width))
y = y.reshape((height, width))
u = u.reshape((height, width))
v = v.reshape((height, width)) #-v if inverted

fig = plt.figure(figsize=(10, 10*height/width))
plt.axis('off')
ax = plt.axes([0, 0, 1, 1], frameon=False)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
ax.invert_yaxis()

#ax.quiver(x, y, u, v)
speed = (u**2 + v**2)**.5
print('Max speed:', speed.max(), 'um/s')
lw = 5*speed / speed.max()
#ax.streamplot(x, y, u, v, color = 'k', linewidth = lw)#, color=U, linewidth=2, cmap='autumn')
#ax.streamplot(x, y, u, v, color=speed/speed.max(), linewidth=lw, cmap='plasma')

ax.pcolormesh(x, y, speed, cmap='inferno', shading='gouraud')
#ax.streamplot(x, y, u, v, color=speed, cmap='inferno')#color='k')
ax.streamplot(x, y, u, v, color='white', arrowsize=2)#color='k')

plt.savefig(output_filename)

plt.show()

