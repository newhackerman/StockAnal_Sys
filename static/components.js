// 现代化UI组件库
class ModernUI {
    constructor() {
        this.init();
    }

    init() {
        this.addParticleBackground();
        this.initScrollAnimations();
        this.initHoverEffects();
        this.initLoadingAnimations();
    }

    // 添加粒子背景效果
    addParticleBackground() {
        const canvas = document.createElement('canvas');
        canvas.id = 'particle-canvas';
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        `;
        document.body.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        let particles = [];
        let animationId;

        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        const createParticle = () => ({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            size: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.2,
            color: Math.random() > 0.5 ? '#0066ff' : '#00d4aa'
        });

        const initParticles = () => {
            particles = [];
            for (let i = 0; i < 50; i++) {
                particles.push(createParticle());
            }
        };

        const updateParticles = () => {
            particles.forEach(particle => {
                particle.x += particle.vx;
                particle.y += particle.vy;

                if (particle.x < 0 || particle.x > canvas.width) {
                    particle.vx = -particle.vx;
                }
                if (particle.y < 0 || particle.y > canvas.height) {
                    particle.vy = -particle.vy;
                }
            });
        };

        const drawParticles = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            particles.forEach(particle => {
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                ctx.fillStyle = particle.color;
                ctx.globalAlpha = particle.opacity;
                ctx.fill();
            });
            
            // 绘制粒子之间的连线
            ctx.globalAlpha = 0.2;
            ctx.strokeStyle = '#0066ff';
            ctx.lineWidth = 0.5;
            
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < 150) {
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
            
            ctx.globalAlpha = 1;
        };

        const animate = () => {
            updateParticles();
            drawParticles();
            animationId = requestAnimationFrame(animate);
        };

        // 初始化
        resizeCanvas();
        initParticles();
        animate();

        // 窗口大小变化时重新调整
        window.addEventListener('resize', () => {
            resizeCanvas();
            initParticles();
        });
    }

    // 滚动动画效果
    initScrollAnimations() {
        const elements = document.querySelectorAll('.fade-in, .slide-in, .zoom-in');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });
        
        elements.forEach(element => {
            observer.observe(element);
        });
    }

    // 悬停效果
    initHoverEffects() {
        const cards = document.querySelectorAll('.card, .hover-lift');
        
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 20;
                const rotateY = (centerX - x) / 20;
                
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
                card.style.transition = 'transform 0.1s';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
                card.style.transition = 'transform 0.5s';
            });
        });
    }

    // 加载动画
    initLoadingAnimations() {
        const loadingElements = document.querySelectorAll('.loading-spinner, .loading-dots');
        
        loadingElements.forEach(element => {
            if (element.classList.contains('loading-spinner')) {
                this.createSpinner(element);
            } else if (element.classList.contains('loading-dots')) {
                this.createDots(element);
            }
        });
    }

    createSpinner(element) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        element.appendChild(spinner);
    }

    createDots(element) {
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'dot';
            dot.style.animationDelay = `${i * 0.15}s`;
            element.appendChild(dot);
        }
    }
}

// 标题行组件 - 优化标题行间距和样式
class TitleBar {
    constructor(options = {}) {
        this.options = {
            selector: '.news-header, .hotspot-header',
            backgroundColor: 'rgba(26, 31, 58, 0.95)',
            textColor: '#ffffff',
            accentColor: '#00d4aa',
            fontSize: '1.1rem',
            padding: '15px 20px',
            borderRadius: '12px 12px 0 0',
            ...options
        };
        
        this.init();
    }
    
    init() {
        const titleBars = document.querySelectorAll(this.options.selector);
        
        titleBars.forEach(titleBar => {
            // 应用样式
            titleBar.style.backgroundColor = this.options.backgroundColor;
            titleBar.style.color = this.options.textColor;
            titleBar.style.padding = this.options.padding;
            titleBar.style.borderRadius = this.options.borderRadius;
            titleBar.style.display = 'flex';
            titleBar.style.alignItems = 'center';
            titleBar.style.justifyContent = 'space-between';
            titleBar.style.borderBottom = `1px solid rgba(255, 255, 255, 0.1)`;
            titleBar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
            
            // 处理标题文本
            const titleElement = titleBar.querySelector('h5');
            if (titleElement) {
                titleElement.style.margin = '0';
                titleElement.style.fontSize = this.options.fontSize;
                titleElement.style.fontWeight = '600';
                titleElement.style.display = 'flex';
                titleElement.style.alignItems = 'center';
                titleElement.style.whiteSpace = 'nowrap'; // 防止标题换行
                titleElement.style.overflow = 'hidden';
                titleElement.style.textOverflow = 'ellipsis';
                
                // 处理图标
                const icon = titleElement.querySelector('i');
                if (icon) {
                    icon.style.color = this.options.accentColor;
                    icon.style.marginRight = '10px';
                    icon.style.fontSize = '1.2em';
                }
            }
        });
    }
}

// 初始化组件
document.addEventListener('DOMContentLoaded', () => {
    // 初始化现代UI组件
    const ui = new ModernUI();
    
    // 初始化标题行组件
    const titleBar = new TitleBar({
        backgroundColor: 'rgba(26, 31, 58, 0.95)',
        textColor: '#ffffff',
        accentColor: '#00d4aa'
    });
});