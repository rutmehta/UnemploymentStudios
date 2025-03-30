// CS Student Job Quest - Main Game File
// A 2D platformer about a computer science student's journey

// Game configuration
const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    parent: 'game-container',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 300 },
            debug: false
        }
    },
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

// Initialize game variables
let player;
let platforms;
let codeSnippets;
let bugs;
let skillPoints = 0;
let cursors;
let scoreText;
let levelText;
let levelName = "Intro to Programming";
let currentLevel = 1;

// Create game instance
const game = new Phaser.Game(config);

// Preload game assets
function preload() {
    // Load images
    this.load.image('sky', 'https://labs.phaser.io/assets/skies/space3.png');
    this.load.image('ground', 'https://labs.phaser.io/assets/sprites/platform.png');
    this.load.image('code', 'https://labs.phaser.io/assets/sprites/star.png');
    this.load.image('bug', 'https://labs.phaser.io/assets/sprites/red_ball.png');
    
    // Loading spritesheet for player character (CS student)
    this.load.spritesheet('student', 
        'https://labs.phaser.io/assets/sprites/dude.png',
        { frameWidth: 32, frameHeight: 48 }
    );
}

// Create game world
function create() {
    // Set background
    this.add.image(400, 300, 'sky');
    
    // Create platforms group
    platforms = this.physics.add.staticGroup();
    
    // Create the ground
    platforms.create(400, 570, 'ground').setScale(2).refreshBody();
    
    // Create some platforms for the level (representing CS concepts)
    platforms.create(600, 400, 'ground');
    platforms.create(50, 250, 'ground');
    platforms.create(750, 220, 'ground');
    
    // Create player character (CS Student)
    player = this.physics.add.sprite(100, 450, 'student');
    player.setBounce(0.2);
    player.setCollideWorldBounds(true);
    
    // Player animations
    this.anims.create({
        key: 'left',
        frames: this.anims.generateFrameNumbers('student', { start: 0, end: 3 }),
        frameRate: 10,
        repeat: -1
    });
    
    this.anims.create({
        key: 'turn',
        frames: [ { key: 'student', frame: 4 } ],
        frameRate: 20
    });
    
    this.anims.create({
        key: 'right',
        frames: this.anims.generateFrameNumbers('student', { start: 5, end: 8 }),
        frameRate: 10,
        repeat: -1
    });
    
    // Set up keyboard input
    cursors = this.input.keyboard.createCursorKeys();
    
    // Create code snippets to collect (representing CS knowledge)
    codeSnippets = this.physics.add.group({
        key: 'code',
        repeat: 11,
        setXY: { x: 12, y: 0, stepX: 70 }
    });
    
    codeSnippets.children.iterate(function (child) {
        child.setBounceY(Phaser.Math.FloatBetween(0.4, 0.8));
    });
    
    // Create bugs (obstacles representing programming errors)
    bugs = this.physics.add.group();
    
    // Create 3 bugs at different positions
    createBug(300, 0, this);
    createBug(500, 0, this);
    createBug(700, 0, this);
    
    // Set up collisions
    this.physics.add.collider(player, platforms);
    this.physics.add.collider(codeSnippets, platforms);
    this.physics.add.collider(bugs, platforms);
    
    // Collect code snippets when player overlaps with them
    this.physics.add.overlap(player, codeSnippets, collectCode, null, this);
    
    // Player loses skill points when hit by bugs
    this.physics.add.collider(player, bugs, hitBug, null, this);
    
    // Update the UI with initial values
    updateUI();
}

// Game loop
function update() {
    // Player movement controls
    if (cursors.left.isDown) {
        player.setVelocityX(-160);
        player.anims.play('left', true);
    }
    else if (cursors.right.isDown) {
        player.setVelocityX(160);
        player.anims.play('right', true);
    }
    else {
        player.setVelocityX(0);
        player.anims.play('turn');
    }
    
    // Jump when the up key is pressed and player is on the ground
    if (cursors.up.isDown && player.body.touching.down) {
        player.setVelocityY(-330);
    }
    
    // Level advancement logic
    if (skillPoints >= 12 && currentLevel === 1) {
        advanceLevel();
    }
}

// Helper function to create a bug
function createBug(x, y, scene) {
    const bug = bugs.create(x, y, 'bug');
    bug.setBounce(1);
    bug.setCollideWorldBounds(true);
    bug.setVelocity(Phaser.Math.Between(-100, 100), 20);
    bug.allowGravity = false;
}

// Collect code snippets and increase skill points
function collectCode(player, codeSnippet) {
    codeSnippet.disableBody(true, true);
    
    // Increase score
    skillPoints += 1;
    
    // Update the UI
    updateUI();
    
    // If all code snippets are collected, create more and a new bug
    if (codeSnippets.countActive(true) === 0) {
        codeSnippets.children.iterate(function (child) {
            child.enableBody(true, child.x, 0, true, true);
        });
        
        // Create a new bug on the opposite side from the player
        const x = (player.x < 400) ? Phaser.Math.Between(400, 800) : Phaser.Math.Between(0, 400);
        createBug(x, 16, this);
    }
}

// Get hit by a bug and lose skill points
function hitBug(player, bug) {
    // Flash the camera to indicate getting hit
    this.cameras.main.flash(300);
    
    // Reduce skill points but don't go below 0
    if (skillPoints > 0) {
        skillPoints -= 1;
        updateUI();
    }
    
    // Reset the bug's position
    bug.setPosition(Phaser.Math.Between(100, 700), 0);
}

// Advance to the next level
function advanceLevel() {
    currentLevel++;
    
    // Change level name based on current level
    switch(currentLevel) {
        case 2:
            levelName = "Advanced Algorithms";
            break;
        case 3:
            levelName = "Internship Experience";
            break;
        case 4:
            levelName = "Final Job Interview";
            break;
        default:
            levelName = "Graduate - You Won!";
    }
    
    // Update the UI
    updateUI();
    
    // Increase difficulty by making bugs faster
    bugs.children.iterate(function (bug) {
        bug.setVelocity(Phaser.Math.Between(-150, 150), 30);
    });
    
    // Alert the player about the level change
    alert("Congratulations! You've advanced to: " + levelName);
}

// Update the UI elements
function updateUI() {
    document.getElementById('sp-count').textContent = skillPoints;
    document.getElementById('level-name').textContent = levelName;
}