const socket = io.connect();

$(() => {
    // ------------------------------------------------------------------------
    //                                                        Initialize Phaser
    // ------------------------------------------------------------------------
    const phaser_config = {
        type: Phaser.AUTO,
        width: window.innerWidth,
        height: window.innerHeight,
        scene: [ SceneLogin ],
        render: {
            'pixelArt': true
        }
    };

    const game = new Phaser.Game(phaser_config);
    game.scene.start('login');


    // ------------------------------------------------------------------------
    //                                                     jQuery Browser Stuff
    // ------------------------------------------------------------------------
    // If the browser gets resized, update the Phaser canvas to match
    $(window).on('resize', () => {
        game.scale.resize(window.innerWidth, window.innerHeight);
    });

    // If the user presses backspace, don't go back in the browser history.
    // Instead, forward the keypress to a relevant scene
    $(document).on('keydown', (e) => {        
        if (e.keyCode == 8) {
           e.preventDefault();

           if (game.scene.isActive('login')) {
               game.scene.getScene('login').keypress(8);
           }
        }
    });
});
