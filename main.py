from flask import Flask, render_template, send_from_directory
from flask.templating import render_template_string
import logging

app = Flask(__name__)

# CSS styles
STYLES = '''
    #canvas {
        border: 1px solid black;
    }
    .colorPicker {
        margin: 10px;
        padding: 10px;
        background: #f0f0f0;
        border-radius: 5px;
    }
    .color-btn {
        margin: 5px;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
'''

# JavaScript animation code
ANIMATION_SCRIPT = '''
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const duckSound = new Audio('static/duck.mp3');
    
    class Circle {
        constructor(startX, startY) {
            this.x = startX;
            this.y = startY;
            this.dx = 4;
            this.dy = 4;
            this.radius = 50;
            this.color = null;
        }
        
        draw() {
            if (this.color) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.strokeStyle = '#00FF00';
                ctx.lineWidth = 2;
                ctx.stroke();
            }
        }
        
        update() {
            if (this.x + this.radius > canvas.width || this.x - this.radius < 0) {
                this.dx = -this.dx;
                playDuckSound();
            }
            if (this.y + this.radius > canvas.height || this.y - this.radius < 0) {
                this.dy = -this.dy;
                playDuckSound();
            }
            
            this.x += this.dx;
            this.y += this.dy;
        }
    }
    
    let circles = [
        new Circle(150, 150),
        new Circle(400, 300)
    ];
    
    let currentBall = 0;
    let animationStarted = false;
    
    function setColor(color) {
        circles[currentBall].color = color;
        document.getElementById(`colorPicker${currentBall}`).style.display = 'none';
        
        // Draw circles immediately after color selection
        drawCircle();
        
        currentBall++;
        if (currentBall < circles.length) {
            document.getElementById(`colorPicker${currentBall}`).style.display = 'block';
        } else {
            startAnimation();
        }
    }
    
    function startAnimation() {
        animationStarted = true;
        drawCircle();
    }
    
    function playDuckSound() {
        duckSound.currentTime = 0;
        duckSound.play();
    }
    
    function drawCircle() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        circles.forEach(circle => {
            circle.draw();
            if (animationStarted) {
                circle.update();
            }
        });
        
        if (animationStarted) {
            requestAnimationFrame(drawCircle);
        }
    }
    
    // Initial draw of static circles
    drawCircle();
'''

@app.route('/')
def draw_circle():
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            {STYLES}
        </style>
    </head>
    <body>
        <div id="colorPicker0" class="colorPicker">
            <h3>Choose a color for the first circle:</h3>
            <button class="color-btn" style="background: #FF0000" onclick="setColor('#FF0000')">Red</button>
            <button class="color-btn" style="background: #FF7F00" onclick="setColor('#FF7F00')">Orange</button>
            <button class="color-btn" style="background: #FFFF00" onclick="setColor('#FFFF00')">Yellow</button>
            <button class="color-btn" style="background: #00FF00" onclick="setColor('#00FF00')">Green</button>
            <button class="color-btn" style="background: #0000FF" onclick="setColor('#0000FF')">Blue</button>
            <button class="color-btn" style="background: #4B0082" onclick="setColor('#4B0082')">Indigo</button>
            <button class="color-btn" style="background: #8F00FF" onclick="setColor('#8F00FF')">Violet</button>
        </div>
        <div id="colorPicker1" class="colorPicker" style="display: none;">
            <h3>Choose a color for the second circle:</h3>
            <button class="color-btn" style="background: #FF0000" onclick="setColor('#FF0000')">Red</button>
            <button class="color-btn" style="background: #FF7F00" onclick="setColor('#FF7F00')">Orange</button>
            <button class="color-btn" style="background: #FFFF00" onclick="setColor('#FFFF00')">Yellow</button>
            <button class="color-btn" style="background: #00FF00" onclick="setColor('#00FF00')">Green</button>
            <button class="color-btn" style="background: #0000FF" onclick="setColor('#0000FF')">Blue</button>
            <button class="color-btn" style="background: #4B0082" onclick="setColor('#4B0082')">Indigo</button>
            <button class="color-btn" style="background: #8F00FF" onclick="setColor('#8F00FF')">Violet</button>
        </div>
        <canvas id="canvas" width="800" height="600"></canvas>
        <script>
            {ANIMATION_SCRIPT}
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(debug=True, port=8000, host='0.0.0.0')
