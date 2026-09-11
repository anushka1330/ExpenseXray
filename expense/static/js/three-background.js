/**
 * Expense X-Ray — Art-Directed 3D Financial Background
 * Luxury Brown, Beige & Cream Palette with Indian Rupee Coins & Banknotes
 * Restrained continuous motion + 5-15px subtle mouse parallax.
 */

(function () {
  'use strict';

  // Check WebGL availability & reduced motion setting
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const canvas = document.getElementById('three-bg-canvas');
  if (!canvas || typeof THREE === 'undefined') return;

  let scene, camera, renderer;
  let coinGroup, noteGroup, particleSystem, gridMesh;
  let mouseX = 0, mouseY = 0;
  let targetMouseX = 0, targetMouseY = 0;
  let windowHalfX = window.innerWidth / 2;
  let windowHalfY = window.innerHeight / 2;

  // Colors adapted for Luxury Brown / Beige / Cream Theme
  const COLOR_BRONZE = 0xd4a373;
  const COLOR_GOLD = 0xe6b87d;
  const COLOR_CREAM = 0xf3e9df;
  const COLOR_BEIGE = 0xc8b9ab;
  const COLOR_DARK = 0x120e0c;

  function createBanknoteTexture(denomination, noteColor, textColor) {
    const cv = document.createElement('canvas');
    cv.width = 512;
    cv.height = 256;
    const ctx = cv.getContext('2d');

    // Background note surface
    ctx.fillStyle = noteColor;
    ctx.fillRect(0, 0, 512, 256);

    // Subtle outer border
    ctx.strokeStyle = textColor;
    ctx.lineWidth = 6;
    ctx.strokeRect(12, 12, 488, 232);

    // Fine guilloche line pattern
    ctx.strokeStyle = textColor + '22';
    ctx.lineWidth = 1;
    for (let i = 0; i < 512; i += 16) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i + 40, 256);
      ctx.stroke();
    }

    // Security thread stripe
    ctx.fillStyle = '#d4a373';
    ctx.fillRect(360, 0, 10, 256);

    // Large ₹ Denomination in center
    ctx.fillStyle = textColor;
    ctx.font = 'bold 64px "Plus Jakarta Sans", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('₹ ' + denomination, 230, 128);

    // Hindi text top-right
    ctx.font = '16px sans-serif';
    ctx.fillText('भारतीय रिज़र्व बैंक', 230, 48);

    // Small serial number
    ctx.font = '14px "JetBrains Mono", monospace';
    ctx.fillText('XR ' + Math.floor(100000 + Math.random() * 900000), 100, 220);

    const texture = new THREE.CanvasTexture(cv);
    texture.minFilter = THREE.LinearFilter;
    return texture;
  }

  function createCoinTexture() {
    const cv = document.createElement('canvas');
    cv.width = 256;
    cv.height = 256;
    const ctx = cv.getContext('2d');

    // Metallic coin surface
    const grad = ctx.createRadialGradient(128, 128, 20, 128, 128, 120);
    grad.addColorStop(0, '#f3e9df');
    grad.addColorStop(0.6, '#d4a373');
    grad.addColorStop(1, '#8c6d4f');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(128, 128, 120, 0, Math.PI * 2);
    ctx.fill();

    // Concentric ring
    ctx.strokeStyle = '#120e0c';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(128, 128, 105, 0, Math.PI * 2);
    ctx.stroke();

    // Embossed ₹ symbol
    ctx.fillStyle = '#120e0c';
    ctx.font = 'bold 110px "Plus Jakarta Sans", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('₹', 128, 134);

    return new THREE.CanvasTexture(cv);
  }

  function init() {
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(COLOR_DARK, 0.025);

    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 100);
    camera.position.z = 18;

    renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));

    // Ambient & Directional Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(COLOR_GOLD, 1.2);
    dirLight1.position.set(10, 15, 10);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(COLOR_CREAM, 0.6);
    dirLight2.position.set(-10, -10, 5);
    scene.add(dirLight2);

    // Group for objects
    coinGroup = new THREE.Group();
    noteGroup = new THREE.Group();
    scene.add(coinGroup);
    scene.add(noteGroup);

    // Generate ₹ Banknotes
    const noteMat1 = new THREE.MeshStandardMaterial({
      map: createBanknoteTexture('500', '#2a221c', '#f3e9df'),
      roughness: 0.4,
      metalness: 0.1,
      side: THREE.DoubleSide
    });
    const noteMat2 = new THREE.MeshStandardMaterial({
      map: createBanknoteTexture('200', '#332921', '#e6b87d'),
      roughness: 0.4,
      metalness: 0.1,
      side: THREE.DoubleSide
    });

    const noteGeo = new THREE.PlaneGeometry(3.6, 1.8);
    const numNotes = window.innerWidth < 768 ? 4 : 8;

    for (let i = 0; i < numNotes; i++) {
      const mesh = new THREE.Mesh(noteGeo, i % 2 === 0 ? noteMat1 : noteMat2);
      mesh.position.set(
        (Math.random() - 0.5) * 22,
        (Math.random() - 0.5) * 14,
        (Math.random() - 0.5) * 12 - 2
      );
      mesh.rotation.set(
        Math.random() * Math.PI,
        Math.random() * Math.PI,
        (Math.random() - 0.5) * 0.5
      );
      mesh.userData = {
        rotSpeedX: (Math.random() - 0.5) * 0.003,
        rotSpeedY: (Math.random() - 0.5) * 0.003,
        floatSpeed: 0.002 + Math.random() * 0.003,
        floatOffset: Math.random() * Math.PI * 2
      };
      noteGroup.add(mesh);
    }

    // Generate ₹ Gold / Bronze Coins
    const coinTexture = createCoinTexture();
    const coinGeo = new THREE.CylinderGeometry(1.1, 1.1, 0.16, 32);
    const coinMat = new THREE.MeshStandardMaterial({
      color: COLOR_BRONZE,
      roughness: 0.35,
      metalness: 0.8,
      map: coinTexture
    });

    const numCoins = window.innerWidth < 768 ? 5 : 10;
    for (let i = 0; i < numCoins; i++) {
      const coin = new THREE.Mesh(coinGeo, coinMat);
      coin.position.set(
        (Math.random() - 0.5) * 24,
        (Math.random() - 0.5) * 16,
        (Math.random() - 0.5) * 10 - 1
      );
      coin.rotation.set(
        Math.PI / 2 + (Math.random() - 0.5) * 0.5,
        Math.random() * Math.PI,
        Math.random() * Math.PI
      );
      coin.userData = {
        rotSpeedX: (Math.random() - 0.5) * 0.005,
        rotSpeedY: (Math.random() - 0.5) * 0.005,
        floatSpeed: 0.003 + Math.random() * 0.003,
        floatOffset: Math.random() * Math.PI * 2
      };
      coinGroup.add(coin);
    }

    // Floating Data Particles
    const particleGeo = new THREE.BufferGeometry();
    const particleCount = window.innerWidth < 768 ? 40 : 90;
    const posArray = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
      posArray[i] = (Math.random() - 0.5) * 30;
      posArray[i + 1] = (Math.random() - 0.5) * 20;
      posArray[i + 2] = (Math.random() - 0.5) * 16;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const particleMat = new THREE.PointsMaterial({
      size: 0.08,
      color: COLOR_GOLD,
      transparent: true,
      opacity: 0.6
    });

    particleSystem = new THREE.Points(particleGeo, particleMat);
    scene.add(particleSystem);

    // Event Listeners
    document.addEventListener('mousemove', onMouseMove, false);
    window.addEventListener('resize', onWindowResize, false);

    if (!prefersReduced) {
      animate();
    } else {
      renderer.render(scene, camera);
    }
  }

  function onMouseMove(event) {
    targetMouseX = (event.clientX - windowHalfX) * 0.0008;
    targetMouseY = (event.clientY - windowHalfY) * 0.0008;
  }

  function onWindowResize() {
    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  let clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);

    const time = clock.getElapsedTime();

    // Smooth subtle mouse parallax (restrained 5-15px movement equivalent)
    mouseX += (targetMouseX - mouseX) * 0.04;
    mouseY += (targetMouseY - mouseY) * 0.04;

    camera.position.x = mouseX * 3;
    camera.position.y = -mouseY * 3;
    camera.lookAt(scene.position);

    // Animate Banknotes
    noteGroup.children.forEach(note => {
      note.rotation.x += note.userData.rotSpeedX;
      note.rotation.y += note.userData.rotSpeedY;
      note.position.y += Math.sin(time * 0.8 + note.userData.floatOffset) * 0.002;
    });

    // Animate Coins
    coinGroup.children.forEach(coin => {
      coin.rotation.x += coin.userData.rotSpeedX;
      coin.rotation.z += coin.userData.rotSpeedY;
      coin.position.y += Math.cos(time * 0.7 + coin.userData.floatOffset) * 0.0025;
    });

    // Slow rotate particle field
    if (particleSystem) {
      particleSystem.rotation.y = time * 0.015;
    }

    renderer.render(scene, camera);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
