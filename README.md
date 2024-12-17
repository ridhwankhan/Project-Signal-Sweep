<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Project Signal Sweep</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            max-width: 800px;
        }
        h1, h2, h3 {
            color: #333;
        }
        a {
            color: #1a0dab;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        pre {
            background-color: #f4f4f4;
            padding: 10px;
            overflow-x: auto;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 4px;
        }
        ul {
            list-style-type: disc;
            margin-left: 20px;
        }
    </style>
</head>
<body>

    <h1>Project Signal Sweep</h1>

    <img src="https://github.com/ridhwankhan/Project-Signal-Sweep/blob/main/images/logo.png?raw=true" alt="Project Logo">

    <h2>Table of Contents</h2>
    <ul>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#features">Features</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#usage">Usage</a></li>
        <li><a href="#screenshots">Screenshots</a></li>
        <li><a href="#technologies-used">Technologies Used</a></li>
        <li><a href="#contributing">Contributing</a></li>
        <li><a href="#license">License</a></li>
        <li><a href="#contact">Contact</a></li>
    </ul>

    <h2 id="introduction">Introduction</h2>

    <p><strong>Project Signal Sweep</strong> is a dynamic radar interface application developed using Python and OpenGL. It scans for nearby Bluetooth devices, visualizes them on a 3D radar display, and provides interactive controls for an enhanced user experience. The application supports multiple themes, making it versatile and user-friendly.</p>

    <h2 id="features">Features</h2>

    <ul>
        <li><strong>Real-Time Bluetooth Scanning:</strong> Detects and displays nearby Bluetooth devices with signal strength indicators.</li>
        <li><strong>3D Radar Visualization:</strong> Interactive 3D radar with smooth sweep animations and device markers.</li>
        <li><strong>Theme Customization:</strong> Choose between Green, Blue, and Orange themes to suit your preference.</li>
        <li><strong>Interactive Controls:</strong>
            <ul>
                <li><strong>Play/Pause Button:</strong> Control the radar sweep animation.</li>
                <li><strong>Close Button:</strong> Exit the application gracefully.</li>
            </ul>
        </li>
        <li><strong>Dynamic Sweep Speed:</strong> Adjust the speed of the radar sweep using keyboard arrow keys.</li>
        <li><strong>Notifications:</strong>
            <ul>
                <li><strong>Device Detected:</strong> Alerts when a new Bluetooth device is found.</li>
                <li><strong>Device Lost:</strong> Notifies when a previously detected device goes out of range.</li>
            </ul>
        </li>
        <li><strong>Screenshot Gallery:</strong> View screenshots of the application in the <a href="https://github.com/ridhwankhan/Project-Signal-Sweep/tree/main/images">Images</a> folder.</li>
    </ul>

    <h2 id="installation">Installation</h2>

    <ol>
        <li><strong>Clone the Repository:</strong>
            <pre><code>git clone https://github.com/ridhwankhan/Project-Signal-Sweep.git
cd Project-Signal-Sweep
</code></pre>
        </li>
        <li><strong>Install Dependencies:</strong>
            <p>Ensure you have Python installed. Then, install the required Python packages:</p>
            <pre><code>pip install simpleaudio
pip install bleak
pip install PyOpenGL
pip install PyOpenGL_accelerate
</code></pre>
        </li>
        <li><strong>Verify Git Installation:</strong>
            <pre><code>git --version
</code></pre>
        </li>
        <li><strong>Ensure <code>beep.wav</code> is Present:</strong>
            <p>Make sure the <code>beep.wav</code> file is located in the root directory of the project. This file is essential for the application's audio notifications.</p>
        </li>
    </ol>

    <h2 id="usage">Usage</h2>

    <ol>
        <li><strong>Run the Application:</strong>
            <pre><code>python "PROJECT SIGNAL SWEEP.py"
</code></pre>
        </li>
        <li><strong>Controls:</strong>
            <ul>
                <li><strong>Play/Pause Sweep:</strong> Click the Play/Pause button at the top-left corner or press the <code>Spacebar</code>.</li>
                <li><strong>Adjust Sweep Speed:</strong> Use the <code>Right Arrow</code> key to increase and the <code>Left Arrow</code> key to decrease the sweep speed.</li>
                <li><strong>Exit Application:</strong> Click the Close (X) button at the top-right corner or press <code>Esc</code>.</li>
            </ul>
        </li>
    </ol>

    <h2 id="screenshots">Screenshots</h2>

    <h3>1. Green Theme</h3>
    <img src="https://github.com/ridhwankhan/Project-Signal-Sweep/blob/main/images/radar.png?raw=true" alt="Green Theme">

    <h3>2. Blue Theme</h3>
    <img src="https://github.com/ridhwankhan/Project-Signal-Sweep/blob/main/images/radar%20red.png?raw=true" alt="Blue Theme">

    <h3>3. Orange Theme</h3>
    <img src="https://github.com/ridhwankhan/Project-Signal-Sweep/blob/main/images/radar%20red.png?raw=true" alt="Orange Theme">

    <h3>4. Device Terminal</h3>
    <img src="https://github.com/ridhwankhan/Project-Signal-Sweep/blob/main/images/device%20terminal.png?raw=true" alt="Device Terminal">

    <h2 id="technologies-used">Technologies Used</h2>

    <ul>
        <li><strong>Python 3.x</strong></li>
        <li><strong>OpenGL</strong></li>
        <li><strong>PyOpenGL</strong></li>
        <li><strong>Bleak (Bluetooth Low Energy)</strong></li>
        <li><strong>SimpleAudio</strong></li>
        <li><strong>GLUT</strong></li>
    </ul>

    <h2 id="contributing">Contributing</h2>

    <p>Contributions are welcome! Please follow these steps:</p>
    <ol>
        <li><strong>Fork the Repository</strong></li>
        <li><strong>Create a New Branch:</strong>
            <pre><code>git checkout -b feature/YourFeature
</code></pre>
        </li>
        <li><strong>Commit Your Changes:</strong>
            <pre><code>git commit -m "Add Your Feature"
</code></pre>
        </li>
        <li><strong>Push to the Branch:</strong>
            <pre><code>git push origin feature/YourFeature
</code></pre>
        </li>
        <li><strong>Open a Pull Request</strong></li>
    </ol>

    <h2 id="license">License</h2>

    <p>This project is licensed under the <a href="https://opensource.org/licenses/MIT">MIT License</a>.</p>

    <h2 id="contact">Contact</h2>

    <p>For any inquiries or feedback, please contact:</p>
    <ul>
        <li><strong>Name:</strong> Ridhwan Khan</li>
        <li><strong>Email:</strong> ridhwankhan@example.com</li>
        <li><strong>GitHub:</strong> <a href="https://github.com/ridhwankhan">ridhwankhan</a></li>
    </ul>

    <hr>

    <p><em>Best of luck with your Project Signal Sweep! :v</em></p>

</body>
</html>
