"use client";
import "@/styles/loading-overlay.css";
import { useState, useEffect, useRef } from "react";

function LoadingOverlay() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const gameStateRef = useRef({
    dinoY: 0,
    dinoVelocity: 0,
    isJumping: false,
    obstacles: [] as { x: number; width: number; height: number }[],
    gameSpeed: 5,
    score: 0,
    frameCount: 0,
  });

  useEffect(() => {
    // Lock scroll when overlay is shown
    document.body.style.overflow = "hidden";

    // Cleanup: restore scroll when component unmounts
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const GROUND_HEIGHT = 150;
    const DINO_WIDTH = 40;
    const DINO_HEIGHT = 50;
    const JUMP_FORCE = -12;
    const GRAVITY = 0.6;

    let animationFrameId: number;

    const jump = () => {
      if (!gameStateRef.current.isJumping && !gameOver) {
        gameStateRef.current.isJumping = true;
        gameStateRef.current.dinoVelocity = JUMP_FORCE;
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space" || e.code === "ArrowUp") {
        e.preventDefault();
        if (gameOver) {
          resetGame();
        } else {
          jump();
        }
      }
    };

    const handleClick = () => {
      if (gameOver) {
        resetGame();
      } else {
        jump();
      }
    };

    const resetGame = () => {
      gameStateRef.current = {
        dinoY: 0,
        dinoVelocity: 0,
        isJumping: false,
        obstacles: [],
        gameSpeed: 5,
        score: 0,
        frameCount: 0,
      };
      setScore(0);
      setGameOver(false);
    };

    const drawDino = () => {
      const dinoX = 50;
      const dinoBottomY = GROUND_HEIGHT - gameStateRef.current.dinoY;
      const primaryColor = getComputedStyle(document.documentElement)
        .getPropertyValue("--primary")
        .trim();

      ctx.fillStyle = `oklch(${primaryColor})`;

      // Body - main torso
      ctx.fillRect(dinoX + 10, dinoBottomY - 45, 30, 22);

      // Neck
      ctx.fillRect(dinoX + 32, dinoBottomY - 50, 8, 10);

      // Head
      ctx.fillRect(dinoX + 32, dinoBottomY - 58, 18, 16);

      // Jaw
      ctx.fillRect(dinoX + 40, dinoBottomY - 50, 10, 8);

      // Eye
      ctx.fillStyle = "#000";
      ctx.fillRect(dinoX + 42, dinoBottomY - 55, 4, 4);

      // Tail
      ctx.fillStyle = `oklch(${primaryColor})`;
      ctx.fillRect(dinoX, dinoBottomY - 45, 12, 10);
      ctx.fillRect(dinoX - 5, dinoBottomY - 40, 10, 6);

      // Arms (tiny)
      ctx.fillRect(dinoX + 15, dinoBottomY - 35, 4, 8);

      // Legs (animated)
      const legAnimation = Math.floor(gameStateRef.current.frameCount / 6) % 2;
      if (!gameStateRef.current.isJumping) {
        // Left leg
        ctx.fillRect(
          dinoX + 12,
          dinoBottomY - 23,
          6,
          legAnimation === 0 ? 18 : 23,
        );
        // Right leg
        ctx.fillRect(
          dinoX + 25,
          dinoBottomY - 23,
          6,
          legAnimation === 1 ? 18 : 23,
        );
      } else {
        // Both legs together when jumping
        ctx.fillRect(dinoX + 12, dinoBottomY - 23, 6, 18);
        ctx.fillRect(dinoX + 25, dinoBottomY - 23, 6, 18);
      }
    };

    const drawObstacles = () => {
      const secondaryColor = getComputedStyle(document.documentElement)
        .getPropertyValue("--secondary")
        .trim();
      ctx.fillStyle = `oklch(${secondaryColor})`;

      gameStateRef.current.obstacles.forEach((obs) => {
        // Main cactus body
        ctx.fillRect(obs.x, GROUND_HEIGHT - obs.height, obs.width, obs.height);

        if (obs.width > 15) {
          // Left arm
          ctx.fillRect(obs.x - 4, GROUND_HEIGHT - obs.height + 12, 4, 15);
          ctx.fillRect(obs.x - 4, GROUND_HEIGHT - obs.height + 12, 8, 4);

          // Right arm
          ctx.fillRect(
            obs.x + obs.width,
            GROUND_HEIGHT - obs.height + 18,
            4,
            12,
          );
          ctx.fillRect(
            obs.x + obs.width - 4,
            GROUND_HEIGHT - obs.height + 18,
            8,
            4,
          );
        } else {
          // Small cactus detail
          ctx.fillRect(
            obs.x + 2,
            GROUND_HEIGHT - obs.height + 5,
            obs.width - 4,
            3,
          );
        }
      });
    };

    const checkCollision = () => {
      const dinoX = 50;
      const dinoBottomY = GROUND_HEIGHT - gameStateRef.current.dinoY;
      const dinoTop = dinoBottomY - DINO_HEIGHT;
      const dinoRight = dinoX + DINO_WIDTH;

      for (const obs of gameStateRef.current.obstacles) {
        const obsLeft = obs.x;
        const obsRight = obs.x + obs.width;
        const obsTop = GROUND_HEIGHT - obs.height;

        if (
          dinoRight > obsLeft + 5 &&
          dinoX < obsRight - 5 &&
          dinoBottomY > obsTop + 5
        ) {
          return true;
        }
      }
      return false;
    };

    const gameLoop = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw ground with theme color
      const borderColor = getComputedStyle(document.documentElement)
        .getPropertyValue("--border")
        .trim();
      ctx.fillStyle = `oklch(${borderColor})`;
      ctx.fillRect(0, GROUND_HEIGHT, canvas.width, 3);

      // Draw dashed ground line
      const mutedColor = getComputedStyle(document.documentElement)
        .getPropertyValue("--muted")
        .trim();
      ctx.fillStyle = `oklch(${mutedColor})`;
      for (let i = 0; i < canvas.width; i += 20) {
        ctx.fillRect(i, GROUND_HEIGHT + 6, 10, 1);
      }

      // Update dino physics
      if (gameStateRef.current.isJumping) {
        gameStateRef.current.dinoVelocity += GRAVITY;
        gameStateRef.current.dinoY -= gameStateRef.current.dinoVelocity;

        if (gameStateRef.current.dinoY <= 0) {
          gameStateRef.current.dinoY = 0;
          gameStateRef.current.dinoVelocity = 0;
          gameStateRef.current.isJumping = false;
        }
      }

      // Spawn obstacles
      gameStateRef.current.frameCount++;
      if (
        gameStateRef.current.frameCount % 90 === 0 &&
        (gameStateRef.current.obstacles.length === 0 ||
          gameStateRef.current.obstacles[
            gameStateRef.current.obstacles.length - 1
          ].x <
            canvas.width - 200)
      ) {
        const height = Math.random() > 0.5 ? 40 : 50;
        const width = Math.random() > 0.7 ? 25 : 15;
        gameStateRef.current.obstacles.push({
          x: canvas.width,
          width,
          height,
        });
      }

      // Update obstacles
      gameStateRef.current.obstacles = gameStateRef.current.obstacles.filter(
        (obs) => {
          obs.x -= gameStateRef.current.gameSpeed;
          return obs.x > -50;
        },
      );

      // Update score
      gameStateRef.current.score += 0.1;
      setScore(Math.floor(gameStateRef.current.score));

      // Increase difficulty
      if (gameStateRef.current.frameCount % 500 === 0) {
        gameStateRef.current.gameSpeed += 0.5;
      }

      drawDino();
      drawObstacles();

      // Check collision
      if (checkCollision()) {
        setGameOver(true);
        return;
      }

      animationFrameId = requestAnimationFrame(gameLoop);
    };

    window.addEventListener("keydown", handleKeyDown);
    canvas.addEventListener("click", handleClick);

    if (!gameOver) {
      gameLoop();
    }

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      canvas.removeEventListener("click", handleClick);
      cancelAnimationFrame(animationFrameId);
    };
  }, [gameOver]);

  return (
    <div className="flex flex-col justify-center items-center fixed inset-0 bg-background/50 z-50">
      <div className="flex flex-col items-center">
        <div className="mb-4 text-3xl font-bold text-primary">
          Score: {score}
        </div>
        <canvas
          ref={canvasRef}
          width={600}
          height={200}
          className="border-2 border-border rounded-lg bg-card shadow-lg cursor-pointer"
        />
        <div className="mt-6 text-center max-w-md">
          <p className="text-sm text-foreground font-medium">
            {gameOver ? (
              <>
                🎮 Game Over! Click or press{" "}
                <span className="font-mono bg-muted text-primary px-2 py-1 rounded">
                  SPACE
                </span>{" "}
                to restart
              </>
            ) : (
              <>
                Press{" "}
                <span className="font-mono bg-muted text-primary px-2 py-1 rounded">
                  SPACE
                </span>{" "}
                or click to jump!
              </>
            )}
          </p>
          <p className="text-xs text-primary mt-3">
            ✈️ Preparing your personalized travel recommendations...
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoadingOverlay;
