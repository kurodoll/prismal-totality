// Handles the game world (rendering) itself

class SceneGUI extends Phaser.Scene {
    constructor() {
        super({ key: 'gui' });

        this.default_font = {
            fontFamily: 'Verdana',
            fontSize: 11,
            color: '#FFFFFF'
        };
    }

    create() {
        const cw = this.sys.game.canvas.width;
        const ch = this.sys.game.canvas.height;

        // Message box
        this.message_box_title = this.add.text(
            cw - 500, 20,
            'Messages',
            {
                fontFamily: 'Verdana',
                fontSize: 15,
                color: '#888888'
            }
        );

        this.message_box_history = []
        this.message_box = this.add.text(
            cw - 480, 40,
            '',
            this.default_font
        );

        this.message('[Local] Connected to server');
    }

    // Adds a message to the message log
    message(msg) {
        this.message_box_history.push(msg);
        this.message_box.text = this.message_box_history.join('\n');
    }
}
