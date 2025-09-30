/**
 * Hyperspeed Background Animation
 * 纯 JavaScript Canvas 实现的超光速星空特效
 * 无需 React 或其他框架依赖
 */

class HyperSpeedBackground {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas element with id "${canvasId}" not found`);
            return;
        }

        this.ctx = this.canvas.getContext('2d');

        // 配置选项
        this.config = {
            starCount: options.starCount || 200,
            speed: options.speed || 2,
            starColor: options.starColor || 'rgba(255, 255, 255, 0.8)',
            trailLength: options.trailLength || 0.3,
            fov: options.fov || 300,
            ...options
        };

        this.stars = [];
        this.centerX = 0;
        this.centerY = 0;

        this.init();
    }

    init() {
        this.resizeCanvas();
        this.createStars();
        this.animate();

        // 响应窗口大小变化
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
    }

    createStars() {
        this.stars = [];
        for (let i = 0; i < this.config.starCount; i++) {
            this.stars.push(this.createStar());
        }
    }

    createStar() {
        return {
            x: Math.random() * this.canvas.width - this.centerX,
            y: Math.random() * this.canvas.height - this.centerY,
            z: Math.random() * this.canvas.width,
            prevX: null,
            prevY: null
        };
    }

    updateStar(star) {
        // 保存上一帧位置用于绘制拖尾
        star.prevX = star.x / star.z * this.config.fov + this.centerX;
        star.prevY = star.y / star.z * this.config.fov + this.centerY;

        // 向前移动
        star.z -= this.config.speed;

        // 如果星星移出屏幕，重置到远处
        if (star.z <= 0) {
            star.x = Math.random() * this.canvas.width - this.centerX;
            star.y = Math.random() * this.canvas.height - this.centerY;
            star.z = this.canvas.width;
            star.prevX = null;
            star.prevY = null;
        }
    }

    drawStar(star) {
        // 3D 投影到 2D
        const x = star.x / star.z * this.config.fov + this.centerX;
        const y = star.y / star.z * this.config.fov + this.centerY;

        // 计算星星大小（近大远小）
        const size = (1 - star.z / this.canvas.width) * 2;

        // 计算星星亮度
        const opacity = (1 - star.z / this.canvas.width) * 0.8;

        // 绘制拖尾效果
        if (star.prevX !== null) {
            this.ctx.beginPath();
            this.ctx.lineWidth = size;
            this.ctx.strokeStyle = `rgba(255, 255, 255, ${opacity * this.config.trailLength})`;
            this.ctx.moveTo(star.prevX, star.prevY);
            this.ctx.lineTo(x, y);
            this.ctx.stroke();
        }

        // 绘制星星本体
        this.ctx.beginPath();
        this.ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
        this.ctx.arc(x, y, size, 0, Math.PI * 2);
        this.ctx.fill();
    }

    animate() {
        // 半透明黑色覆盖，创建拖尾效果
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // 更新和绘制所有星星
        this.stars.forEach(star => {
            this.updateStar(star);
            this.drawStar(star);
        });

        // 继续动画循环
        requestAnimationFrame(() => this.animate());
    }

    // 动态调整速度
    setSpeed(speed) {
        this.config.speed = speed;
    }

    // 销毁动画
    destroy() {
        window.removeEventListener('resize', this.resizeCanvas);
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

// 导出供全局使用
window.HyperSpeedBackground = HyperSpeedBackground;