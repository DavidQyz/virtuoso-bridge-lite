import numpy as np
import matplotlib.pyplot as plt

f = 13.56e6
T = 1 / f
Vmax = 5

t = np.linspace(0, 2*T, 1000)
sine_full = Vmax * np.sin(2 * np.pi * f * t)
sine_half = np.maximum(sine_full, 0)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

v_out = 2.5
t_start = np.arcsin(v_out / Vmax) / (2 * np.pi * f)

# Vc 较低 → pulse 较长
pulse_width1 = 25e-9
t_end1 = t_start + pulse_width1

ax1.plot(t * 1e9, sine_half, 'b', linewidth=1.5)
ax1.axhline(v_out, color='g', linestyle=':', linewidth=1, label='Vout')
ax1.axvline(t_start * 1e9, color='gray', linestyle='--', linewidth=1.2)
ax1.axvline(t_end1 * 1e9, color='gray', linestyle='--', linewidth=1.2)
ax1.fill_between(t * 1e9, sine_half, v_out,
                  where=(t >= t_start) & (t <= t_end1) & (sine_half > v_out),
                  alpha=0.3, color='orange', label='Charging')
ax1.set_ylabel('Voltage (V)')
ax1.set_title('Lower Vc → Longer charging time')
ax1.legend(loc='upper right')
ax1.set_xlim([0, 2*T*1e9])

# Vc 较高 → pulse 较短
pulse_width2 = 10e-9
t_end2 = t_start + pulse_width2

ax2.plot(t * 1e9, sine_half, 'b', linewidth=1.5)
ax2.axhline(v_out, color='g', linestyle=':', linewidth=1)
ax2.axvline(t_start * 1e9, color='gray', linestyle='--', linewidth=1.2)
ax2.axvline(t_end2 * 1e9, color='gray', linestyle='--', linewidth=1.2)
ax2.fill_between(t * 1e9, sine_half, v_out,
                  where=(t >= t_start) & (t <= t_end2) & (sine_half > v_out),
                  alpha=0.3, color='orange')
ax2.set_xlabel('Time (ns)')
ax2.set_ylabel('Voltage (V)')
ax2.set_title('Higher Vc → Shorter charging time')
ax2.set_xlim([0, 2*T*1e9])

plt.tight_layout()
plt.show()