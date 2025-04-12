import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange, config
import time

# Configura Numba per massime prestazioni
config.THREADING_LAYER = 'threadsafe'

# ===========================================
# PARAMETRI DI SIMULAZIONE
# ===========================================
N = 500                # Numero di elettroni
m = 50                   # Massa delle particelle
L = 100.0               # Scala del sistema
T = 2/m                 # Temperatura ridotta
steps = 20000            # Passi totali MC
step_size = 1           # Massimo spostamento
eps = 1e-7              # Softening per evitare divergenze
np.random.seed(44)      # Riproducibilità

# Calcolo parametro lb
lb = np.sqrt(L**2/(N*6.28*m))

# Parametri per la funzione di correlazione (PCF)
pcf_r_max = L/2        
pcf_dr = 0.1           
pcf_bins = int(pcf_r_max/pcf_dr)

# ===========================================
# FUNZIONI NUMBA-OTTIMIZZATE
# ===========================================
def compute_hexatic_order(pos):
    psi6 = 0j
    for i in range(N):
        angles = []
        for j in range(N):
            if i != j:
                dx = pos[j,0] - pos[i,0]
                dy = pos[j,1] - pos[i,1]
                r = np.sqrt(dx**2 + dy**2)
                if r < 1.2 * (L/np.sqrt(N)):  # Raggio primo vicino
                    angle = np.arctan2(dy, dx)
                    angles.append(angle)
        if angles:
            psi6_i = np.mean(np.exp(1j * 6 * np.array(angles)))
            psi6 += psi6_i
    return np.abs(psi6/N)

@njit(nogil=True, fastmath=True)
def distance_matrix(pos, L):
    """Calcola la matrice delle distanze con condizioni periodiche"""
    n = pos.shape[0]
    dmat = np.empty((n, n), dtype=np.float64)
    for i in prange(n):
        for j in prange(n):
            dx = pos[j,0] - pos[i,0]
            dy = pos[j,1] - pos[i,1]
            
            dmat[i,j] = np.sqrt(dx**2 + dy**2 + eps)
    return dmat

@njit(nogil=True, parallel=True)
def total_energy(pos, lb, m, L):
    """Calcola l'energia totale in parallelo"""
    energy = 0.0
    n = pos.shape[0]
    for i in prange(n):
        for j in prange(i+1, n):
            dx = pos[j,0] - pos[i,0]
            dy = pos[j,1] - pos[i,1]
            
            r = np.sqrt(dx**2 + dy**2 + eps)
            energy += -m**2 * np.log(r/lb)
    
    harmonic = (m/(4*lb**2)) * np.sum(pos**2)
    return energy + harmonic

@njit(nogil=True, fastmath=True)
def delta_energy(pos, idx, new_pos, lb, m, L):
    """Calcola la differenza di energia per una mossa"""
    delta = 0.0
    old_pos = pos[idx].copy()
    n = pos.shape[0]
    
    for j in prange(n):
        if j == idx:
            continue
            
        # Vecchia distanza
        dx = pos[j,0] - old_pos[0]
        dy = pos[j,1] - old_pos[1]
        
        r_old = np.sqrt(dx**2 + dy**2 + eps)
        
        # Nuova distanza
        dx = pos[j,0] - new_pos[0]
        dy = pos[j,1] - new_pos[1]
        
        r_new = np.sqrt(dx**2 + dy**2 + eps)
        
        delta += -m**2 * (np.log(r_new/lb) - np.log(r_old/lb))
    
    # Termine armonico
    delta += (m/(4*lb**2)) * (np.sum(new_pos**2) - np.sum(old_pos**2))
    return delta

@njit(nogil=True, parallel=True)
def mc_step(pos, step_size, lb, m, L, T):
    """Esegue un passo MC parallelo"""
    n = pos.shape[0]
    accepted = 0
    total_delta = 0.0
    
    # Esegui mosse in parallelo
    for i in prange(n):
        idx = np.random.randint(n)
        current_pos = pos[idx].copy()
        displacement = (np.random.rand(2) - 0.5) * step_size
        new_pos = (current_pos + displacement) 
        
        delta = delta_energy(pos, idx, new_pos, lb, m, L)
        
        if delta < 0 or np.random.rand() < np.exp(-delta/T):
            pos[idx] = new_pos
            accepted += 1
            total_delta += delta
    
    return total_delta, accepted

@njit(nogil=True, parallel=True)
def compute_psi3(pos, L, cutoff_scale=1.4):
    """Calcola ψ₃ in parallelo"""
    psi3_total = 0.0j
    avg_neighbors = 0.0
    n = pos.shape[0]
    cutoff = cutoff_scale * (L/np.sqrt(n))
    
    for i in prange(n):
        angles = []
        for j in prange(n):
            if i == j:
                continue
            dx = pos[j,0] - pos[i,0]
            dy = pos[j,1] - pos[i,1]
            r = np.sqrt(dx**2 + dy**2)
            if r < cutoff:
                angle = np.arctan2(dy, dx)
                angles.append(angle)
        
        if angles:
            psi3_i = np.mean(np.exp(1j * 3 * np.array(angles)))
            psi3_total += psi3_i
            avg_neighbors += len(angles)
    
    psi3_abs = np.abs(psi3_total/n)
    avg_neighbors /= n
    return psi3_abs, avg_neighbors

@njit(nogil=True, parallel=True)
def compute_pcf(pos, L, r_max, dr):
    """Calcola la funzione di correlazione in parallelo"""
    bins = int(r_max/dr)
    hist = np.zeros(bins)
    n = pos.shape[0]
    
    for i in prange(n):
        for j in prange(i+1, n):
            dx = pos[j,0] - pos[i,0]
            dy = pos[j,1] - pos[i,1]
            
            r = np.sqrt(dx**2 + dy**2)
            if r < r_max:
                bin_idx = int(r/dr)
                if bin_idx < bins:
                    hist[bin_idx] += 2
    return hist

# ===========================================
# INIZIALIZZAZIONE SISTEMA
# ===========================================
positions = np.loadtxt('/Users/mfiaschi/Desktop/posizione500.txt')#np.random.rand(N, 2) * L - L/2
positions_initial = positions.copy()

# ===========================================
# CICLO MONTE CARLO PARALLELO
# ===========================================
energy = total_energy(positions, lb, m, L)
pcf_histogram = np.zeros(pcf_bins)
start_time = time.time()
acceptance_history = []

for step in range(steps):
    delta, accepted = mc_step(positions, step_size, lb, m, L, T)
    energy += delta
    acceptance_rate = accepted/N
    acceptance_history.append(acceptance_rate)
    
    # Campionamento PCF
    if step > 1000 and step % 100 == 0:
        hist = compute_pcf(positions, L, pcf_r_max, pcf_dr)
        pcf_histogram += hist
     # Adattazione dinamica dello step size
    #if step % 500 == 0 and step > 100:
     #   if acceptance_rate < 0.25:
      #      step_size *= 0.999
       # elif acceptance_rate > 0.45:
        #    step_size *= 1.001
  
    # Output
    if step % 2000 == 0:
        psi3, avg_neigh = compute_psi3(positions, L)
        hex_order = compute_hexatic_order(positions)  # Implementare similmente a compute_psi3
        print(f"Step {step}/{steps} | E: {energy:.1f} | Acc: {acceptance_rate:.2f} | "
              f"ψ₃: {hex_order:.2f} | Vicini: {avg_neigh:.1f} | "
              f"Tempo: {time.time()-start_time:.1f}s")

# ===========================================
# ANALISI FINALE
# ===========================================
r_values = (np.arange(pcf_bins) + 0.5) * pcf_dr
density = N / (np.pi * L**2)
normalization = density * N * np.pi * ((r_values + pcf_dr/2)**2 - (r_values - pcf_dr/2)**2)
g_r = pcf_histogram / (normalization + 1e-9)

# Visualizzazione
plt.figure(figsize=(15,10))
plt.subplot(131, aspect='equal')
plt.scatter(positions[:,0], positions[:,1], s=1)
plt.title("Configurazione Finale")


plt.subplot(132, aspect='equal')
plt.scatter(positions_initial[:,0], positions_initial[:,1], s=1)
plt.title("Configurazione Iniziale")


plt.show()

plt.figure(figsize=(15,5))
plt.subplot(131)
plt.plot(r_values, g_r)
plt.axhline(1, c='k', ls='--')
plt.title("Funzione di Correlazione Radiale")

plt.tight_layout()
plt.show()

print(f"\nSimulazione completata in {time.time()-start_time:.1f} secondi")
print(f"Accettazione media: {np.mean(acceptance_history):.2f}")
print(f"Energia finale/particella: {energy/N:.3f}")
