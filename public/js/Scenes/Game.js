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
                    = level.level.tiles[y * level.level.width + x];

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
        this.renderSprites();
    }

    // Finds sprites in entities and renders them
    renderSprites() {
        for (let i = 0; i < this.level.entities.length; i++) {
            if ('sprite' in this.level.entities[i].components) {
                const pos_x
                    = this.level.entities[i].components.position.x
                    * this.level.level.tile_width;

                const pos_y
                    = this.level.entities[i].components.position.y
                    * this.level.level.tile_height;

                // If the entity already has a sprite image defined, just
                //     update it
                if (this.level.entities[i].image) {
                    this.level.entities[i].image.x = pos_x;
                    this.level.entities[i].image.y = pos_y;
                } else {
                    this.level.entities[i].image =
                        this.add.sprite(pos_x, pos_y, 'player').setOrigin(0, 0);
                }
            }
        }
    }

    // Given updated entity data, updates those entities locally
    updateEntities(updates) {
        for (let i = 0; i < updates.length; i++) {
            let match_found = false;

            for (let j = 0; j < this.level.entities.length; j++) {
                if (updates[i].id == this.level.entities[j].id) {
                    match_found = true;

                    // If the entity has been marked inactive, we'll delete it
                    //     a bit later
                    if (!updates[i].active) {
                        this.level.entities[j].active = false;
                        break;
                    }

                    // Update data individually, so that data that has been
                    //     added locally isn't wiped away
                    this.level.entities[j].components = updates[i].components;

                    break;
                }
            }

            if (!match_found) {
                // Must be a new entity
                this.level.entities.push(updates[i]);
            }
        }

        // Now remove no longer active entities entirely
        for (let i = this.level.entities.length - 1; i >= 0; i--) {
            if (!this.level.entities[i].active) {
                if (this.level.entities[i].image) {
                    this.level.entities[i].image.destroy();
                }

                this.level.entities.splice(i, 1);
            }
        }

        // Update the image itself for sprite entities
        this.renderSprites();
    }
}
