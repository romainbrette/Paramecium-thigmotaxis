'''
A food conditioning model of thigmotaxis
'''
from brian2 import *

defaultclock.dt = 1*second
N = 100 # number of cells

detachment_rate = 0.005*Hz
z_decay = 20*60*second
z_threshold = 0.5 # above this threshold, we consider that the association between food and attachment is strong
attachment_decay = 60*second
attachment_increase = 0.001*Hz/(60*second)

eqs = '''
attached : 1
dattachment_rate/dt = int(z>z_threshold)*(1-attached)*attachment_increase - int(z<z_threshold)*attached*attachment_rate/attachment_decay : 1/second
dz/dt = -attached*z/z_decay : 1     # association variable
'''

cells = NeuronGroup(N, eqs, threshold='rand()<attachment_rate*dt*(1-attached) + detachment_rate*dt*attached',
            reset='attached = 1-attached')
cells.z = 1

# Dummy group to store averages at every time step
averager = NeuronGroup(1, '''attached : 1
                                       attachment_rate : Hz
                                       z : 1''')
averager_synapses = Synapses(cells, averager, '''attached_post = attached_pre/N : 1 (summed)
                                                        attachment_rate_post = attachment_rate_pre/N : 1/second (summed)
                                                        z_post = z_pre/N : 1 (summed)''')
averager_synapses.connect()
M = StateMonitor(averager, ['attached', 'attachment_rate', 'z'], record=True)

run(60*60*second)

figure()
subplot(311)
plot(M.t/(60*second), 1 - M.attached[0], 'k')
ylim(0, 1)
ylabel("Proportion of swimming cells")
subplot(312)
plot(M.t/(60*second), M.attachment_rate[0], 'k')
ylabel("Attachment rate (Hz)")
subplot(313)
plot(M.t/(60*second), M.z[0], 'r')
ylim(0, 1)
ylabel('z')
xlabel("Time (min)")
tight_layout()
show()
