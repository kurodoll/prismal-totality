// The Login Scene handles the initial interface before entering the game
//     itself

class SceneLogin extends Phaser.Scene {
    constructor() {
        super({ key: 'login' });
    }

    preload() {
        this.load.image('login bg', '/graphics/art/login_bg.jpg');

        this.load.script(
            'webfont',
            'https://ajax.googleapis.com/ajax/libs/webfont/1.6.26/webfont.js'
        );
    }

    create() {
        const cw = this.sys.game.canvas.width;

        // Render and scale the login background image to fill the screen
        this.img_login_bg = this.add.image(0, 0, 'login bg').setOrigin(0, 0);
        this.img_login_bg.displayWidth = cw;
        this.img_login_bg.scaleY = this.img_login_bg.scaleX;

        // Render the game title
        const this_add = this.add;

        WebFont.load({
            google: {
                families: [ 'Macondo Swash Caps' ]
            },
            active: function() {
                const title = this_add.text(
                    cw / 2, 100,
                    'Prismal Totality',
                    {
                        fontFamily: 'Macondo Swash Caps',
                        fontSize: 100,
                        color: '#FFFFFF'
                    }
                ).setShadow(0, 0, "#FFFFFF", 5, false, true);

                // Set text position by its center
                title.setOrigin(0.5);
            }
        });
    }
}
