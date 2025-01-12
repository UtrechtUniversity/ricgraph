# Ricgraph in a container
This page describes how to install and run Ricgraph in a 
[Podman container](https://podman.io).
A container is like a small box that holds an application and everything 
it needs to run, such as files and settings. It
makes sure the application works the same on any computer. 
Podman is a tool for creating and running containers, and it
is safe because it doesn’t need special permissions to work. 
This makes it a good choice for running programs quickly and reliably.

Other Ricgraph install options are:
* [Install and configure
  Ricgraph for a single user](ricgraph_install_configure.md).
* [Install and configure
  Ricgraph as a server](ricgraph_as_server.md).
 
To install and run Ricgraph in a Podman container, 
follow these steps:
* [Read the notes on the Ricgraph Podman container](#notes-on-the-ricgraph-podman-container).
* [Install Podman](#install-podman).
* [Install and run the Ricgraph Podman container](#install-and-run-the-ricgraph-podman-container).
* [Optional: Advanced use of the Ricgraph Podman container](#advanced-use-of-the-ricgraph-podman-container).

[Return to main README.md file](../README.md).


## Notes on the Ricgraph Podman container
Warning: Do not use the Ricgraph Podman container in a production environment,
since it does not provide a web server (such as Apache).
If you would like to harvest a lot of items, you are better off using 
[Ricgraph for a single user](ricgraph_install_configure.md) or
[Ricgraph as a server](ricgraph_as_server.md).
The Ricgraph Podman container is ideal for instructional or personal use.

The Ricgraph Podman container has been designed in such a way that it is easy to use.
This also means that some "good container design practices" have not been followed,
in particular:
* the harvested items are stored in the Ricgraph Podman container (usually, one would use
  data storage in the filesystem on the host);
* Neo4j Community Edition and Ricgraph are in the same Ricgraph Podman container
  (usually, one would use separate containers).

So, do not use the Ricgraph Podman container in a production environment.


## Install Podman
Only for this step you will need *Administrator* or *root* access on
your machine.
Choose one of the following:
* Linux:
  * [Install command line version 
    Podman](https://podman.io/docs/installation#installing-on-linux).
  * [Install GUI version Podman 
    Desktop](https://podman-desktop.io/docs/installation/linux-install).
* MacOS:
  * [Install command line version
    Podman](https://podman.io/docs/installation#macos).
  * [Install GUI version Podman
    Desktop](https://podman-desktop.io/docs/installation/macos-install).
* Windows:
  * [Install command line version
    Podman](https://podman-desktop.io/docs/installation/windows-install#installing-podman).
  * [Install GUI version Podman
    Desktop](https://podman-desktop.io/docs/installation/windows-install#installing-podman-desktop).
  
  The following information might help you installing Podman on Windows. Note that
  you will need *Administrator* privileges.
  * For both the command line version as well as the Desktop GUI version of Podman, you will need
    *Windows Subsystem for Linux (WSL) 2*. Install it as follows:
    * Open a *PowerShell (Admin)* or *Terminal (Admin)*. 
    * Type:
      ```
      dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
      wsl --install --no-distribution
      ```

  Next, for the command line version of Podman:
  * Get Podman from the GitHub releases page https://github.com/containers/podman/releases, choose the latest
    version with file name extension .msi.
  * Install it by clicking on the downloaded file, follow the instructions.
  * Exit your *Administator* privileges.
  * Open Windows *PowerShell* or *Terminal* and use the commands in the sections below.

  Or, for the Desktop GUI version of Podman:
  * Follow the instructions from [Install GUI version Podman
    Desktop](https://podman-desktop.io/docs/installation/windows-install#installing-podman-desktop).
  * You might get a Windows Firewall message, asking "Do you want to allow public, private, and
    domain networks to access this app?". Choose *Private networks* from the list and click "Allow".
  * After installation of the Desktop GUI version of Podman,
    you will need to make a Virtual Machine to run Podman. Podman Desktop
    will ask you to do this. Follow the instructions.
  * I got a weird error during installation, but rebooting my Windows machine resolved it.
    Try it, if you get a similar message.
  * Note that Podman Desktop GUI also installs Podman command line version.
  * Exit your *Administator* privileges.
  * Open Windows *PowerShell* or *Terminal* and use the commands in the sections below.
  * Or use Podman Desktop GUI to pull the Ricgraph image (for location see below) and
    to start it.


## Install and run the Ricgraph Podman container
For the following commands, you will need a *Terminal* or *Command line* or
*PowerShell* window. If you use the Podman Windows command line version, 
first start *Windows Subsystem for Linux (WSL)* by typing `wsl` in the Windows
*Terminal* or *PowerShell* window.

The Ricgraph container is hosted on the 
GitHub Container repository https://ghcr.io/utrechtuniversity/ricgraph.

There are two ways to run the Ricgraph Podman container:
1. You have not done a `podman commit` (see below).

   Run the latest (newest) version of the Ricgraph Podman container, and download it if you don't have it:
   ```
   podman run --pull=newer --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
   ```
   If you get an error like 
   *Error: creating container storage: the container name "ricgraph" is already in use*, type:
   ```
   podman run --pull=newer --replace --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
   ```

2. You have done a `podman commit` (see below).

   Run the local version of the Ricgraph Podman container
   (do not use the `--pull=newer` flag):
   ```
   podman run --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
   ```
   If you get an error like
   *Error: creating container storage: the container name "ricgraph" is already in use*, type:
   ```
   podman run --replace --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
   ```

 Starting the container takes about ten seconds.
 Explore items with Ricgraph Explorer,
 in your browser, go to http://localhost:3030.

If you started `podman run` for the first time, 
the container does not have data in it. You can observe this by going to the 
Ricgraph Explorer home page (http://localhost:3030),
and by scrolling down to the "About Ricgraph" section.
The easiest method for getting data in it, is to run the `batch_harvest_demo.py` script
that harvests a selection of research information of Utrecht University. 
The script harvests from both
the data repository [Yoda](https://www.uu.nl/en/research/yoda)
and from the 
[Research Software Directory](https://research-software-directory.org)
These two repositories do not need authentication keys.
Running this script will take several minutes to complete.
Type
```
podman exec -it ricgraph python batch_harvest_demo.py
```

It is a design decision to store all harvested items in the Ricgraph container
(see [Notes on the Ricgraph Podman 
container](#notes-on-the-ricgraph-podman-container)),
so make them permanent (i.e. also available after restart of the container)
by typing:
```
podman commit ricgraph ghcr.io/utrechtuniversity/ricgraph:latest
```

Now restart the Ricgraph container to see the results:
```
podman restart ricgraph
```
Explore the harvested items with Ricgraph Explorer,
in your browser, go to http://localhost:3030.

You can stop all containers by typing:
```
podman stop -a
```
To (re)start, use the `podman run` command above.

## Advanced use of the Ricgraph Podman container
For the following commands, you will need a *Terminal* or *Command line* or
*PowerShell* window. If you use the Podman Windows command line version, 
first start *Windows Subsystem for Linux (WSL)* by typing `wsl` in the Windows
*Terminal* or *PowerShell* window.

Get the status of all containers:
```
podman ps
```

Remove all podman containers:
```
podman rmi -a -f
```

Use a `bash` shell "in" the Ricgraph Podman container:
```
podman exec -it ricgraph /bin/bash
```

To harvest other sources then 
[Yoda](https://www.uu.nl/en/research/yoda)
and the 
[Research Software Directory](https://research-software-directory.org),
you will need to modify the Ricgraph Podman container. You might need to add API keys
to the [Ricgraph initialization file 
*ricgraph.ini*](ricgraph_install_configure.md#ricgraph-initialization-file).
Follow these steps:
* First execute a `bash` shell in the Ricgraph Podman container (see above). Execute the
  following commands in the container (in the bash shell you just started).
* If necessary, add API keys to *ricgraph.ini*. It is in */usr/local* in the container.
  You can use `vim` (or `vi`) to edit it.
* Go to the directory with harvest scripts:
  ```
  cd /app/ricgraph/harvest
  ```
* Run a harvest script (they start with 'harvest_'):
  ```
  python [name of harvest script]
  ```
  or create your own harvest script.
  For more information, read [Ricgraph harvest scripts](ricgraph_harvest_scripts.md).
* Make the data permanent in the container, see `podman commit` above.  
  Note that the size of your container may explode if you harvest a lot of items.
* Restart the container, see `podman restart` above.

For other useful commands, read the comment section of the [Containerfile](../Containerfile).
