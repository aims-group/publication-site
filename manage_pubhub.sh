# Constants
PUBHUB_CONFIG=pubhub_config
DEFAULT_EDITOR=vim
CONFIG_DIR=pubhub_configs
BACKUP_DIR=$CONFIG_DIR/backups
BACKUP_FORMAT=config_backup_$(date +'%F_%I-%M-%S')

set -e

#Custom functions
function configure() {
    mkdir -p $BACKUP_DIR
    cp $CONFIG_DIR/$PUBHUB_CONFIG $BACKUP_DIR/$BACKUP_FORMAT
    $DEFAULT_EDITOR $CONFIG_DIR/$PUBHUB_CONFIG
    saveConfigs $CONFIG_DIR/$PUBHUB_CONFIG
}

# Saves config to required directories
# Arg1 name of config file to copy into active locations
function saveConfigs() {
    cp $CONFIG_DIR/$PUBHUB_CONFIG traefik/.env
    cp $CONFIG_DIR/$PUBHUB_CONFIG .envs/.prod.env
}

function setCurrentConfig() {
    clear
    fileCount=$(ls "$BACKUP_DIR" | wc -l)
    if [ "$fileCount" -lt "1" ]; then
        echo "There aren't any config files in the backup directory."
        read -p "Press enter to continue..." option
        return
    fi

    echo "Enter the config backup to restore (1 -"$fileCount"):"
    ls $BACKUP_DIR/ | sort -r | cat -n
    read configNum
    fileName=$(ls "$BACKUP_DIR" | sort -r | sed -n "$configNum"p)
    configName=$(pwd)/$BACKUP_DIR/$fileName

    if test -f "$configName"; then
        echo "Setting $fileName as current..."
        cp $CONFIG_DIR/$PUBHUB_CONFIG $BACKUP_DIR/$BACKUP_FORMAT
        cp $configName $CONFIG_DIR/$PUBHUB_CONFIG
        saveConfigs
        echo "Done!"
    else
        clear
        echo "The config file number entered was invalid."
        read -p "Try again? (y/n): " option
        if [ "$option" = "y" ]; then
            setCurrentConfig
        fi
    fi
}

#Arg1 name of service to start: pubhub or traefik
#Arg2 optional '-d' to perform service in background
function startService() {
    echo "Starting $1"
    cd $1
    docker compose -f docker-compose.prod.yml up --build $2
    cd ..
}

#Arg1 name of service top stop: pubhub or traefik
function stopService() {
    echo "Stopping $1"
    cd $1
    docker compose -f docker-compose.prod.yml down --remove-orphans
    cd ..
}

#Arg1 name of service to start: pubhub or traefik
#Arg2 optional '-d' to perform service in background
function startLocalService() {
    echo "Starting $1"
    cd $1
    docker compose -f docker-compose.yml up --build $2
    cd ..
}

#Arg1 name of service top stop: pubhub or traefik
function stopLocalService() {
    echo "Stopping $1"
    cd $1
    docker compose -f docker-compose.yml down --remove-orphans
    cd ..
}

function startPubhubContainers() {
    clear
    saveConfigs $CONFIG_DIR/$PUBHUB_CONFIG
    startService traefik -d
    startService pubhub -d
}

function stopPubhubContainers() {
    clear
    stopService pubhub
    stopService traefik
}

function toggleLocalContainers() {
    clear
    # Stop any remaining services and start them up again
    stopLocalService pubhub -d
    startLocalService pubhub -d
}

# Main Menu
function mainMenu() {
    echo "Main Menu Options:"
    echo "1 Configure Pubhub"
    echo "2 Restore Backup Config"
    echo "3 Start all containers"
    echo "4 Stop all containers"
    echo "5 Start / Stop Local Dev Containers"
    echo "6 Container Start / Stop Menu"
    echo "7 Exit"
    read option
    if [ -z $option ]; then
        clear
        echo "Please enter a number corresponding to the menu item."
        mainMenu
    else
        if [ "$option" = "1" ]; then
            configure
            clear
            mainMenu
        elif [ "$option" = "2" ]; then
            setCurrentConfig
            clear
            mainMenu
        elif [ "$option" = "3" ]; then
            startPubhubContainers
            clear
            mainMenu
        elif [ "$option" = "4" ]; then
            stopPubhubContainers
            clear
            mainMenu
        elif [ "$option" = "5" ]; then
            toggleLocalContainers
            clear
            mainMenu
        elif [ "$option" = "6" ]; then
            clear
            containersMenu
        elif [ "$option" = "7" ]; then
            clear
            return 0
        else
            clear
            echo "You entered: $option"
            echo "Please enter a number from 1 to 6"
            mainMenu
        fi
    fi
}

#Container Menu
function containersMenu() {
    echo "Container Start/Stop"
    echo "1 Start PubHub"
    echo "2 Stop PubHub"
    echo "3 Start Traefik"
    echo "4 Stop Traefik"
    echo "5 Start Documentation"
    echo "6 Stop Documentation"
    echo "7 Back to Main Menu"
    read option
    if [ -z $option ]; then
        clear
        echo "Please enter a number corresponding to the menu item."
        containersMenu
    else
        if [ "$option" = "1" ]; then
            startService pubhub
            mainMenu
        elif [ "$option" = "2" ]; then
            stopService pubhub
            clear
            mainMenu
        elif [ "$option" = "3" ]; then
            startService traefik
            mainMenu
        elif [ "$option" = "4" ]; then
            stopService traefik
            clear
            mainMenu
        elif [ "$option" = "5" ]; then
            startLocalService docs -d
            mainMenu
        elif [ "$option" = "6" ]; then
            stopLocalService docs -d
            clear
            mainMenu
        elif [ "$option" = "7" ]; then
            clear
            mainMenu
        else
            clear
            echo "You entered: $option"
            echo "Please enter a number from 1 to 7"
            containersMenu
        fi
    fi
}

clear
mainMenu
