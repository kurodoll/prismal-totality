const socket = io.connect();

$(() => {
    // ------------------------------------------------------------------------
    //                                                        Initialize Phaser
    // ------------------------------------------------------------------------
    const phaser_config = {
        type: Phaser.AUTO,
        width: window.innerWidth,
        height: window.innerHeight,
        scene: [],
        render: {
            'pixelArt': true
        }
    };

    const game = new Phaser.Game(phaser_config);


    // ------------------------------------------------------------------------
    //                                                     jQuery Browser Stuff
    // ------------------------------------------------------------------------
    // If the browser gets resized, update the Phaser canvas to match
    $(window).on('resize', () => {
        game.scale.resize(window.innerWidth, window.innerHeight);
    });
});
