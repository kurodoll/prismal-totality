const socket = io.connect();

$(() => {
    // ------------------------------------------------------------------------
    //                                                        Initialize Phaser
    // ------------------------------------------------------------------------
    const phaser_config = {
        type: Phaser.AUTO,
        width: window.innerWidth,
        height: window.innerHeight,
        scene: [ SceneLogin, SceneGUI, SceneGame ],
        render: {
            'pixelArt': true
        }
    };

    const game = new Phaser.Game(phaser_config);
    game.scene.start('game'); // Begin preloading actual game assets (HACK)
    game.scene.switch('game', 'login');


    // ------------------------------------------------------------------------
    //                                                    Socket.io Interaction
    // ------------------------------------------------------------------------
    socket.on('login success', () => {
        // Switch to the GUI and Game scenes
        game.scene.switch('login', 'gui');
        game.scene.start('game');

        // Since we've just logged in, we want the data of the level that our
        //     player is on. If our player is a new player, the server will
        //     set us up at a starting area
        socket.emit('request present level');
    });

    // Server has sent us the data for the level we are one
    socket.on('present level', (level) => {
        // Forward the data to the Game scene to render the level
        game.scene.getScene('game').setLevel(level);
    });


    // ------------------------------------------------------------------------
    //                                                     jQuery Browser Stuff
    // ------------------------------------------------------------------------
    // If the browser gets resized, update the Phaser canvas to match
    $(window).on('resize', () => {
        game.scale.resize(window.innerWidth, window.innerHeight);
    });

    // If the user presses backspace, don't go back in the browser history.
    //     Instead, forward the keypress to a relevant scene
    $(document).on('keydown', (e) => {        
        if (e.keyCode == 8) {
           e.preventDefault();

           if (game.scene.isActive('login')) {
               game.scene.getScene('login').keypress(8);
           }
        }
    });
});
