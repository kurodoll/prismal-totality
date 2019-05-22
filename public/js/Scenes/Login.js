// The Login Scene handles the initial interface before entering the game
//     itself

class SceneLogin extends Phaser.Scene {
    constructor() {
        super({ key: 'login' });

        this.default_font = {
            fontFamily: 'Verdana',
            fontSize: 11,
            color: '#FFFFFF'
        };

        // Create a list of characters that are valid for text input
        this.valid_keys = [ 32 ]; // 32 = Space
        for (let i = 48; i <= 57; i++) { // Numbers 0-9
            this.valid_keys.push(i);
        }
        for (let i = 65; i <= 90; i++) { // Characters a-z
            this.valid_keys.push(i);
        }
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
                this_add.text(
                    cw / 2, 100,
                    'Prismal Totality',
                    {
                        fontFamily: 'Macondo Swash Caps',
                        fontSize: 100,
                        color: '#FFFFFF'
                    }
                ).setShadow(0, 0, "#FFFFFF", 5, false, true)
                 .setOrigin(0.5);
            }
        });

        // Render login prompt
        this.add.text(
            cw / 2, 200,
            'Type a username and press Enter to login',
            this.default_font
        ).setShadow(1, 1, "#000000", 0, false, true)
         .setOrigin(0.5);

        this.input_box = this.add.graphics();
        this.input_box.fillStyle(0x000000, 0.5);
        this.input_box.fillRect(cw / 2 - 100, 210, 200, 20);

        this.username_entry = this.add.text(
            cw / 2, 220,
            '',
            {
                fontFamily: 'Verdana',
                fontSize: 11,
                color: '#FFCC88'
            }
        ).setShadow(1, 1, "#000000", 0, false, true)
         .setOrigin(0.5);

        // Listen for key presses and fill in inputs
        this.active_element = 'username';

        this.input.keyboard.on('keydown', (key) => {
            if (this.active_element == 'username') {
                // Check whether the pressed key is valid to enter
                if (this.valid_keys.indexOf(key.keyCode) > -1) {
                    // Max username length is 20 characters
                    if (this.username_entry.text.length < 20) {
                        this.username_entry.text += key.key;
                    }
                }

                // If the user presses enter, log them in
                else if (key.keyCode == 13) {
                    socket.emit('login', this.username_entry.text);
                }
            }
        });
    }

    // Used for forwarding special keypresses from elsewhere
    keypress(key_code) {
        if (key_code == 8) {
            // Backspace the active element
            if (this.active_element == 'username') {
                this.username_entry.text
                    = this.username_entry.text.slice(0, -1);
            }
        }
    }
}
