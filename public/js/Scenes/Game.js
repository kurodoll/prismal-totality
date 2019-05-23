// Handles all interface elements during gameplay

class SceneGame extends Phaser.Scene {
    constructor() {
        super({ key: 'game' });
    }

    preload() {
        this.load.image('tileset test', '/graphics/tilesets/test');
        this.load.json('tileset test data', '/data/tilesets/test');
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
    }
}
