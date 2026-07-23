# Paramecium-thigmotaxis
These are scripts to analyze data and produce the figures of the paper.

Data must first be downloaded on Zenodo.
The path to data must then be specified in the file /figures/figures.py.
The paper-specific scripts are in `figures` and `scripts`. Other folders contain various
functions to analyze trajectories, manipulate movies, make user interfaces, etc.


figures/
    fig*/
        All scripts to generate figures.
    figures.py
        Functions to make bar plots and calculate statistics.
        IMPORTANT: the variable data_path stores the path to the data, it must be specified.

interface/
    Various functions for user interfaces.

movie/
    Classes to manipulate movie files.

scripts/
    beating/
        Analysis of ciliary beating.
        batch_frequency_map.py
            Calculates the main beating frequency at all positions in a set of movie files (.tiff).
        extract_stable_interval_and_process.py
            Extracts a stable interval in a movie and calculates average image and variation image.
        spectrum_select.py
            Calculates the frequency spectrum in a given ROI, from a .tiff movie.
    file_management/
        convert_to_mp4.py
            Convert .czi and .tiff movies files to mp4, with a few options downscaling options.
        extract_fps.py
            Extracts the frame rate from .czi and .tiff files.
    piv/
        average_piv.py
            Particle image velocimetry. Produces a text file with the average vector field.
        plot_piv.py
            Displays the PIV vector field.
    attachment_count.py
        Counts attached and swimming cells from two trajectory files (background, and background-subtracted).
    attachment_count_drop.py
        Same, but an ROI is calculated by image segmentation of the drop (useful when there are many artifacts such as droplets around the drop).
    calculate_features.py
        Calculates various features (speed, etc.) from a raw trajectory file.
    play_trajectories.py
        Displays an animation of trajectories from a trajectory file.
    swimming_analysis.py
        Shows the number of swimming cells as a function of time, as well as speed and avoiding reaction rate.
    track.py
        Generates tracks from an unlinked trajectory file.

stats/
    A few statistical functions.

trajectories/
    Manipulation of trajectory files and analysis of trajectories.
    fasttrack.py
        Loading Fasttrack files (https://fasttrack.sh).
    linking.py
        Linking identified cells through frames into tracks, using norfair and trackpy.
    magic_loading.py
        Loads trajectories files with various formats.
    trajectory_analysis.py
        Many functions to analyze trajectories.
    visualization.py
        Plotting trajectories.