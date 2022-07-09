# Spotify Playlist Generator

This is an advanced playlist generator for Spotify meant to provide the user with lots of control. There is a sample playlist script in `playlists/background.toml` (one of my main ones I listen to).

## Use

Clone the repository, then rename `sample_config.toml` to `config.toml` and configure it. You will need to set up a Spotify application and set the redirect URL to the one within `config.toml`.

After the application is set up, run `main.py`. Follow the instructions in console to gain the token for the API.

Once that is done a list of links should appear. To import them copy the links of all and paste it into a Spotify Playlist.

Go ahead and configure the playlist file until you come up with a script that suits you.

## How it works

To generate a playlist the program creates a list of 'instructions' to carry out. This is what is within the `<playlist>.toml` file. These instructions can do many things such as get liked tracks, similar tracks, recommendations, and more.
