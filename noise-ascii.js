#!/usr/bin/env node
const { makeNoise2D } = require('open-simplex-noise');

const colors = {
  reset: '\x1b[0m',
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  brightBlack: '\x1b[90m',
  brightRed: '\x1b[91m',
  brightGreen: '\x1b[92m',
  brightYellow: '\x1b[93m',
  brightBlue: '\x1b[94m',
  brightMagenta: '\x1b[95m',
  brightCyan: '\x1b[96m',
  brightWhite: '\x1b[97m'
};

function generateOrbAnimation(width = 80, height = 24, scale = 0.1, seed = Date.now(), timeOffset = 0) {
  const noise = makeNoise2D(seed);

  let output = '';

  const centerX = width / 2;
  const centerY = height / 2;
  const baseRadius = Math.min(width, height) / 2 * 1.2;

  // Pulsing effect
  const pulse = Math.sin(timeOffset * 1.5) * 0.2 + 1;
  const orbRadius = baseRadius * pulse;

  // Rotation angles (like donut.js)
  const A = timeOffset * 0.8; // X-axis rotation
  const B = timeOffset * 0.5; // Y-axis rotation
  const cosA = Math.cos(A);
  const sinA = Math.sin(A);
  const cosB = Math.cos(B);
  const sinB = Math.sin(B);

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const dx = (x - centerX) * 0.5; // Compress horizontally to reduce left/right margins
      const dy = (y - centerY) * 1.8; // Slight vertical compression for better sphere appearance
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance > orbRadius) {
        output += ' ';
      } else {
        // Calculate position on sphere surface
        const sphereDepth = Math.sqrt(Math.max(0, orbRadius * orbRadius - distance * distance));
        const normalizedDistance = distance / orbRadius;

        // 3D sphere coordinates (before rotation)
        const sphereX = dx;
        const sphereY = dy;
        const sphereZ = sphereDepth;

        // Apply 3D rotation (like donut.js)
        const rotatedX = sphereX * cosB - sphereZ * sinB;
        const rotatedY = sphereY * cosA + (sphereX * sinB + sphereZ * cosB) * sinA;
        const rotatedZ = -sphereY * sinA + (sphereX * sinB + sphereZ * cosB) * cosA;

        // Multiple noise layers for complexity (using rotated coordinates)
        const surfaceNoise = noise(
          rotatedX * scale * 2 + timeOffset * 0.8,
          rotatedY * scale * 2 + Math.cos(timeOffset * 1.2) * 0.4
        );

        const detailNoise = noise(
          rotatedX * scale * 8 + timeOffset * 1.5,
          rotatedZ * scale * 8 + Math.sin(timeOffset * 0.9) * 0.3
        ) * 0.3;

        const radialNoise = noise(
          rotatedY * scale * 3 + timeOffset * 0.6,
          Math.atan2(rotatedZ, rotatedX) * 2 + timeOffset
        ) * 0.4;

        // Combine noise layers
        const combinedNoise = surfaceNoise + detailNoise + radialNoise;

        // Create sphere lighting effect with rotation-aware shading
        const lightingFactor = Math.pow(1 - normalizedDistance, 1.5);
        const depthShading = (rotatedZ + orbRadius) / (2 * orbRadius); // Rotation-aware depth

        // Final intensity calculation
        const intensity = ((combinedNoise + 1) / 2) * lightingFactor * depthShading * 1.3;

        // Soft edges with falloff
        const edgeFalloff = Math.pow(1 - normalizedDistance, 0.5);
        const finalIntensity = intensity * edgeFalloff;

        if (finalIntensity > 0.1) {
          // Create shape patterns based on noise and position
          const shapeChoice = getShapeCharacter(finalIntensity, rotatedX, rotatedY, rotatedZ, timeOffset);

          const color = getOrbColor(finalIntensity, normalizedDistance, timeOffset);
          output += color + shapeChoice + colors.reset;
        } else {
          output += ' ';
        }
      }
    }
    output += '\n';
  }

  return output;
}

function getShapeCharacter(intensity, x, y, z, time) {
  // Define keyboard symbol sets
  const math = '+-=*/';
  const brackets = '()[]{}<>';
  const symbols = '#$%&@!?';
  const marks = '.,;:\'"`~';

  // Use position and time to determine symbol type
  const symbolType = Math.floor((Math.sin(x * 0.3 + time * 0.5) + 1) * 2) % 4;
  const patternShift = Math.sin(y * 0.4 + z * 0.2 + time * 0.7) + 1;

  let symbolSet;
  switch (symbolType) {
    case 0: symbolSet = math; break;
    case 1: symbolSet = brackets; break;
    case 2: symbolSet = symbols; break;
    default: symbolSet = marks; break;
  }

  // Select character based on intensity and pattern
  const charIndex = Math.floor((intensity + patternShift * 0.3) * symbolSet.length);
  return symbolSet[Math.min(charIndex, symbolSet.length - 1)];
}

function getOrbColor(intensity, distance, time) {
  // Dynamic color shifting inspired by Bluey's warm palette
  const hueShift = Math.sin(time * 0.4) * 0.5 + 0.5;
  const warmShift = Math.cos(time * 0.2 + distance) * 0.5 + 0.5;

  if (intensity < 0.15) return colors.brightBlack;
  if (intensity < 0.25) return colors.blue;
  if (intensity < 0.35) {
    return hueShift > 0.6 ? colors.magenta : colors.blue;
  }
  if (intensity < 0.45) {
    return warmShift > 0.7 ? colors.yellow : colors.cyan;
  }
  if (intensity < 0.55) {
    return hueShift > 0.5 ? colors.brightYellow : colors.brightCyan;
  }
  if (intensity < 0.65) {
    return warmShift > 0.6 ? colors.brightMagenta : colors.brightYellow;
  }
  if (intensity < 0.75) {
    return hueShift > 0.4 ? colors.red : colors.yellow;
  }
  if (intensity < 0.85) {
    return warmShift > 0.5 ? colors.brightRed : colors.brightMagenta;
  }
  return hueShift > 0.3 ? colors.brightWhite : colors.brightYellow;
}

function generateASCIINoise(width = 80, height = 24, scale = 0.1, seed = Date.now(), timeOffset = 0) {
  return generateOrbAnimation(width, height, scale, seed, timeOffset);
}

function animateNoise() {
  let frame = 0;
  const animate = () => {
    // Get terminal dimensions
    const terminalWidth = process.stdout.columns || 80;
    const terminalHeight = process.stdout.rows || 24;

    // Reserve space for header (2 lines)
    const availableHeight = terminalHeight - 2;

    // Use full terminal dimensions with minimal padding
    const width = Math.max(40, terminalWidth);
    const height = Math.max(10, availableHeight);

    const timeOffset = frame * 0.05;
    const asciiNoise = generateASCIINoise(width, height, 0.08, 42, timeOffset);

    // Move cursor to top and overwrite for smoother animation
    process.stdout.write('\x1b[H');
    process.stdout.write(colors.brightWhite + '🔮 Animated OpenSimplex Orb ✨' + colors.reset + '\n');
    process.stdout.write(colors.brightBlack + 'Press Ctrl+C to exit\n' + colors.reset);
    process.stdout.write(asciiNoise);

    frame++;
    setTimeout(animate, 80);
  };
  animate();
}

if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.includes('--animate')) {
    animateNoise();
  } else {
    const width = parseInt(args.find(arg => arg.startsWith('--width='))?.split('=')[1]) || 80;
    const height = parseInt(args.find(arg => arg.startsWith('--height='))?.split('=')[1]) || 24;
    const scale = parseFloat(args.find(arg => arg.startsWith('--scale='))?.split('=')[1]) || 0.1;
    const seed = parseInt(args.find(arg => arg.startsWith('--seed='))?.split('=')[1]) || Date.now();

    console.log('OpenSimplex Noise ASCII Visualization\n');
    console.log(generateASCIINoise(width, height, scale, seed, 0));
    console.log('\nOptions:');
    console.log('  --animate           Animated noise');
    console.log('  --width=80          Width of output');
    console.log('  --height=24         Height of output');
    console.log('  --scale=0.1         Noise scale (smaller = more zoomed out)');
    console.log('  --seed=12345        Seed for reproducible noise');
  }
}

module.exports = { generateASCIINoise };
