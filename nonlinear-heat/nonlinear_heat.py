import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def F(u, prev, c, k, dk):

    f = np.zeros(len(u))

    for i in range(len(u)):
        # du and ddu represent the differences used to approximate derivatives
        if i==0:
            du = u[i+1]
            ddu = ( - 2*u[i] + u[i+1])

            f[i] = prev[i] - u[i] - c*( 0.25*dk(u[i]) * du**2 + k(u[i]) * ddu )
            
        elif i==len(u)-1:
            du = -u[i-1]
            ddu = (u[i-1] - 2*u[i])

            f[i] = prev[i] - u[i] - c*( 0.25*dk(u[i]) * du**2 + k(u[i]) * ddu )
            
        else:
            du = (u[i+1] - u[i-1])
            ddu = (u[i-1] - 2*u[i] + u[i+1])

            f[i] = prev[i] - u[i] - c*( 0.25*dk(u[i]) * du**2 + k(u[i]) * ddu )
    
    return f


def generate_jacobian(u, c, k, dk, ddk):

    n = len(u)
    J = np.zeros([n, n])

    for i in range(n):
        # du and ddu represent the differences used to approximate derivatives
        if i==0:
            du = u[i+1]
            ddu = ( - 2*u[i] + u[i+1])

            J[i][i] = 1 - c*(0.25*ddk(u[i])*du + dk(u[i])*ddu - 2*k(u[i]))
            
            J[i][i+1] = -c*(0.5*dk(u[i])*du + k(u[i]))        

        elif i==n-1:
            du = -u[i-1]
            ddu = (u[i-1] - 2*u[i])

            J[i][i-1] = c*(0.5*dk(u[i])*du - k(u[i]))

            J[i][i] = 1 - c*(0.25*ddk(u[i])*du + dk(u[i])*ddu - 2*k(u[i]))
            
        else:
            du = (u[i+1] - u[i-1])
            ddu = (u[i-1] - 2*u[i] + u[i+1])

            J[i][i-1] = c*(0.5*dk(u[i])*du - k(u[i]))

            J[i][i] = 1 - c*(0.25*ddk(u[i])*du + dk(u[i])*ddu - 2*k(u[i]))
            
            J[i][i+1] = -c*(0.5*dk(u[i])*du + k(u[i]))

    return J


def newton_step(u, J, c, k, dk):

    n = len(u)
    u_prev = u
    u_next = u

    for i in range(100):
        u_prev = u_next
        u_next -= np.linalg.solve(J, F(u, u_next, c, k, dk))

        if np.linalg.norm(u_prev - u_next) < 1e-9 * n:
            break

    return u_next


def run_heat_sim(u0, a, b, dt, nx, nt, k, dk, ddk):
    # inputs:
    # u0: function defining the initial heat distribution
    # a: left endpoint
    # b: right endpoint
    # dt: timestep 
    # nx: number of points for spatial discretization
    # nt: number of timesteps to run for
    # k: the function specifying the thermal diffusivity
    # dk: derivative of k
    # ddk: derivative of dk
    #
    # output:
    # displays the evolution of the solution using matplotlib


    x = np.linspace(a, b, nx+2, endpoint=True)
    u = np.array([u0(t) for t in x[1:-1]])
    t = 0.0  
    dx = x[1] - x[0]
    c = dt/dx**2

    upper_bound = max(u) * 1.1
    lower_bound= min(u) * 1.1
    fig, ax = plt.subplots()

    for i in range(nt):
        J = generate_jacobian(u, c, k, dk, ddk)
        u = newton_step(u, J, c, k, dk)
        t += dt

        time_label = str(np.round(t, 5))
        ax.clear()
        ax.set_ylim(bottom=lower_bound, top=upper_bound)
        ax.plot(x, [0] + list(u) + [0], color='b', label='nonlinear: k=0.5/(1 + u^2)')
        ax.legend()
        ax.set_title('Time={}'.format(time_label))
        plt.pause(0.01)


def heat_compare_gif(u0, a, b, dt, nx, nt, k, dk, ddk, filename='heat_sim.gif'):
    # inputs:
    # u0: function defining the initial heat distribution
    # a: left endpoint
    # b: right endpoint
    # dt: timestep 
    # nx: number of points for spatial discretization
    # nt: number of timesteps to run for
    # k: the function specifying the thermal diffusivity
    # dk: derivative of k
    # ddk: derivative of dk
    #
    # output:
    # creates a gif of the evolution of the normal heat equation and the given nonlinear variant

    x = np.linspace(a, b, nx+2, endpoint=True)
    u = np.array([u0(t) for t in x[1:-1]])
    t = 0.0
    baseline = np.array([u0(t) for t in x[1:-1]])
    
    dx = x[1] - x[0]
    c = dt/dx**2

    A = np.zeros([nx, nx])
    for i in range(nx):
        A[i][i] = 1 + 2*c
        if i != 0:
            A[i][i-1] = -c
        if i != nx-1:
            A[i][i+1] = -c 

    upper_bound = max(u) * 1.1
    lower_bound= min(u) * 1.1

    fig, ax = plt.subplots()

    def update_plot(frame):
        nonlocal u, t, baseline
        for i in range(3):
            J = generate_jacobian(u, c, k, dk, ddk)
            u = newton_step(u, J, c, k, dk)
            baseline = np.linalg.solve(A, baseline)
            t += dt

        time_label = str(np.round(t, 5))

        ax.clear()
        ax.set_ylim(bottom=lower_bound, top=upper_bound)
        ax.plot(x, [0] + list(u) + [0], color='b', label='nonlinear: k=0.5/(1 + u^2)')
        ax.plot(x, [0] + list(baseline) + [0], color='r', label='linear: k=1')
        ax.legend()
        ax.set_title('Time={}'.format(time_label))

    ani = FuncAnimation(fig, update_plot, frames=nt, repeat=False)

    ani.save(filename=filename, writer='pillow', fps=60)


def nonlinear_heat_gif():
    return
