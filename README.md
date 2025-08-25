# Animated Fungal Network Growth

Created by Isin Kosemen, in collaboration with Dr. Carlos A. Aguilar-Trigueros, this project presents an interactive, timelapse visualization of fungal mycelial network growth. Designed at the intersection of computational biology, data visualization, and digital art, the application animates the temporal unfolding of fungal networks from empirically derived structural data.

The visualization system preloads per-frame CSV datasets—including vertices, edges, and spatial coordinates—for multiple fungal species and reconstructs their progressive growth as a timelapse animation of mycelial expansion. Each edge in the network can be colored dynamically according to either its chronological emergence (time-sequence mode using the perceptually uniform Viridis palette) or by quantitative edge attributes such as hyphal width, resistance, or length. A fully customizable color scheme and responsive legend support both exploratory analysis and aesthetic curation.

This work can be situated both as a scientific tool—to study and compare structural-functional trade-offs in fungal networks—and as a form of data-driven media art, where the hidden geometries of fungal life are revealed through algorithmic storytelling. It embodies a hybrid approach: a living archive of fungal morphogenesis and a curatorial platform for visual experimentation.

This project is built with React for interactivity, D3.js for scientific data visualization, and Canvas rendering for high-performance animation, bundled with Vite and styled using Tailwind CSS. Together, these technologies enable the seamless integration of biological data with interactive, real-time visual storytelling.
