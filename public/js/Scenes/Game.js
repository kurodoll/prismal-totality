// Handles all interface elements during gameplay

class SceneGame extends Phaser.Scene {
    constructor() {
        super({ key: 'game' });
    }

    preload() {
        this.load.image('tileset test', '/graphics/tilesets/test');
        this.load.json('tileset test data', '/data/tilesets/test');

        this.load.image('player', '/graphics/sprite/player')
    }

    create() {
        // Set up inputs
        const movement_keys = [ '1', '2', '3', '4', '6', '7', '8', '9' ];

        this.input.keyboard.on('keydown', (e) => {
            if (movement_keys.indexOf(e.key) > -1) {
                socket.emit(
                    'action',
                    'move',
                    { 'dir': e.key }
                );
            }
        });
    }

    setLevel(level) {
        this.level = level;

        // Create a map of tiles that will be rendered
        this.map = this.make.tilemap({
            tileWidth: level.level.tile_width,
            tileHeight: level.level.tile_height,
            width: level.level.width,
            height: level.level.height
        });

        // Set the map to use the specified tileset
        this.tileset = this.map.addTilesetImage(
            'tileset ' + level.level.tileset,
            'tileset ' + level.level.tileset,
            level.level.tile_width,
            level.level.tile_height,
            0, 0
        );

        // Get the specified tileset data which maps tile type to its index in
        //     the tileset image
        const tileset_json_name = 'tileset ' + level.level.tileset + ' data';
        this.tileset_data = this.cache.json.get(tileset_json_name);

        // This is needed for rendering to work?
        this.layer = this.map.createBlankDynamicLayer('Layer 1', this.tileset);

        // Go through each tile in the level and render it
        for (let x = 0; x < level.level.width; x++) {
            for (let y = 0; y < level.level.height; y++) {
                const tile_type
                    = level.level.tiles[y * level.level.height + x];

                const tileset_index = this.tileset_data[tile_type];

                this.map.putTileAt(tileset_index, x, y);
            }
        }

        // Center the map and zoom to the specified zoom amount for this level.
        // Small maps can zoom in (by default) so that it doesn't appear weird
        //     to the user, or large maps can start zoomed out
        this.cameras.main.centerOn(
            (level.level.width * level.level.tile_width) / 2,
            (level.level.height * level.level.tile_height) / 2
        );

        this.cameras.main.setZoom(level.level.camera_zoom);

        // Now handle the entities present on the level
        for (let i = 0; i < level.entities.length; i++) {
            if ('sprite' in level.entities[i].components) {
                const pos_x
                    = this.level.entities[i].components.position.x
                    * this.level.level.tile_width;

                const pos_y
                    = this.level.entities[i].components.position.y
                    * this.level.level.tile_height;

                this.level.entities[i].image =
                    this.add.sprite(pos_x, pos_y, 'player').setOrigin(0, 0);
            }
        }
    }

    // Given updated entity data, updates those entities locally
    updateEntities(updates) {
        for (let i = 0; i < updates.length; i++) {
            for (let j = 0; j < this.level.entities.length; j++) {
                if (updates[i].id == this.level.entities[j].id) {
                    // Update data individually, so that data that has been
                    //     added locally isn't wiped away
                    this.level.entities[j].components = updates[i].components;

                    // If this entity has an image (sprite), it needs to be
                    //     updated to reflect the data changes
                    if (this.level.entities[j].image) {
                        const pos_x
                            = this.level.entities[j].components.position.x
                            * this.level.level.tile_width;

                        const pos_y
                            = this.level.entities[j].components.position.y
                            * this.level.level.tile_height;

                        this.level.entities[j].image.x = pos_x;
                        this.level.entities[j].image.y = pos_y;
                    }

                    break;
                }
            }
        }
    }
}
