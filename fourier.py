'''
Minimal working example of a low-pass filter using fourier transform, to remind me how that works.
'''

import numpy as np
import matplotlib.pyplot as plt


class Fourier:

    def __init__(self, time_steps, signal):
        '''
        Constructs a Fourier object from a 1D-signal.

        :param time_steps: x-values at which the signal is sampled
        :param signal: y-values of the signal
        '''

        self.time_steps = time_steps
        self.signal = signal

        n = signal.size
        sampling_rate = n / (time_steps[-1] - time_steps[0])
        print("Created Fourier object with sampling rate: ", sampling_rate)  # how many samples we drop for every 1 step of distance

        # run Fourier transform
        amps = np.fft.fft(signal)
        freqs = np.fft.fftfreq(n, d=1/sampling_rate)

        self.amps = amps
        self.freqs = freqs
        self.filtered = dict()  # will contain filtered frequencies

        # create list containing amplitude-frequency pairs, ignoring the zero-frequency 
        pairs = []
        self.zero_comp = amps[0], freqs[0]
        for amplitude, frequency in zip(amps[1:], freqs[1:]):
            pairs.append([amplitude, frequency]) # amplitude is complex, frequency is real

        # sort the pairs descending by magnitude of amplitude
        pairs = list(reversed(sorted(pairs, key=lambda v: np.sqrt(v[0].real**2 + v[0].imag**2))))
        self.pairs = np.array(pairs)


    def filter(self, num):
        """
        Retains only the num largest amplitudes.

        :param num: number of amplitudes to keep
        """

        # by default, set all frequencies to 0
        for freq in self.freqs:
            self.filtered[freq] = 0.0

        # set the amplitude of the zero-frequency
        self.filtered[self.zero_comp[1]] = self.zero_comp[0]

        # set the amplitudes of the biggest num frequencies
        for amp, freq in self.pairs[:num]:
            self.filtered[freq] = amp


    def inverse(self):
        '''
        Calculate inverse fourier transform from filtered frequencies.
        '''

        wave = []
        for f in self.freqs:
            wave.append(self.filtered[f])
        wave = np.array(wave)

        res = np.fft.ifft(wave)

        return res


def vis_signal(time_steps, signal, title):
    '''
    Visualizes a signal by plotting it.

    :param time_steps: the x-values of the signal
    :param signal: the y-values of the signal
    :param title: the title of the plot
    '''

    # plotting signal in time domain
    plt.figure(figsize=(10, 5))
    plt.plot(time_steps, signal)
    plt.xlim(time_steps[0], time_steps[-1])
    plt.xlabel("time")
    plt.ylabel("signal")
    plt.title(title)
    plt.show()


def main():
    '''
    Generates a noisy signal by adding some zero-centered gaussian noise 
    to a base signal constructed from adding clean sine and cosine waves.

    Visualizes the original signal.
    
    Performs fourier transform and filters the frequencies to apply
    low-pass filtering which should remove the noise.

    Visualizes the cleaned signal.
    '''

    start = 0           # where the sequence starts
    stop = 10           # where the sequence stops
    num = 450           # how many sample points are included
    frequencies = 10    # how many frequencies to keep

    time_steps = np.linspace(start, stop, num, endpoint=True) # basically x-values for the signal

    data = [2*np.sin(x)+np.cos(x+0.5*np.pi) + np.random.normal(0, 0.15) for x in time_steps] # basically y-values for the signal
    
    signal = np.array(data, dtype=float)

    vis_signal(time_steps, signal, 'Original Signal in Time Domain')

    fou = Fourier(time_steps, signal)

    fou.filter(frequencies)

    clean_signal = fou.inverse()

    vis_signal(time_steps, clean_signal.real, 'Reproduced Signal in Time Domain')


if __name__ == "__main__":

    main()
