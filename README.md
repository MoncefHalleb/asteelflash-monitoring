
# AsteelFlash Internship Project – Quality Dashboard

This repository contains the codebase for my **2-month internship project at AsteelFlash**, a leading Electronics Manufacturing Services (EMS) company. The project focuses on developing a **Quality Dashboard** to monitor and manage critical quality metrics for PCB (Printed Circuit Board) production.

🗓 **Internship Period:** May 07, 2025 – July 07, 2025  
🏭 **Company:** AsteelFlash

---

## 🚀 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Future Improvements](#future-improvements)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## 📈 Project Overview

During my internship, I designed and implemented a responsive web application to enhance AsteelFlash’s quality control processes. The dashboard offers:

✅ **Real-time insights** into production quality.  
✅ **Role-based access control** for secure administration.  
✅ A sleek, **dark-themed user interface** optimized for both desktop and mobile.

---

## ✨ Features

- **User Authentication:** Secure login with role-based permissions (admin/user).  
- **Quality Dashboard:** Visualizes metrics like total, good, bad quantities, and defect breakdowns using interactive charts.  
- **Admin Panel:** Enables admins to add, modify, and manage board data and users.  
- **Interactive Tables:** Search, sort, and paginate through board data.  
- **Modern UI:** Glassmorphism effects, animated loaders, and a dynamic background.  
- **Mobile Friendly:** Collapsible menus and responsive design.

---

## ⚙️ Tech Stack

- **Frontend:** Svelte + Tailwind CSS
- **Backend:** Python + Fast API
- **Visualization:** Chart.js  
- **Icons:** Remixicon  
- **Auth:** Custom Svelte store-based authentication  + JWT secured by Python 
- **Build Tool:** SvelteKit, Node.js  
- **Version Control:** Git, GitHub

---

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/asteelflash-internship.git
cd asteelflash-internship
```

### 2. Install dependencies
Make sure you have Node.js installed, then run:
```bash
npm install
```

### 3. Configure environment variables
Create a `.env` file in the root directory and add:
```env
VITE_API_URL=http://api.asteelflash.local
VITE_AUTH_TOKEN=your-auth-token
```
> ⚠️ **Note:** Do not commit `.env` to version control. Keep credentials secure.

### 4. Run the development server
```bash
npm run dev
```
Then navigate to [http://localhost:5173](http://localhost:5173).

---

## 🚀 Usage

- **Login:** Go to `/login` with provided credentials.  
- **Dashboard:** Access `/dashboard` to view production quality metrics.  
- **Admin Panel:** For admins, visit `/admin` and `/register` to manage boards and users.  
- **Logout:** Use the logout button in the header.

---

## 📁 File Structure

```bash
asteelflash-internship/
├── src/
│   ├── lib/         # Utility functions (API calls)
│   ├── stores/      # Svelte stores (authStore, etc.)
│   ├── routes/      # Pages (dashboard, login, admin)
│   └── app.svelte   # Root component
├── static/          # Static assets (images, icons)
├── .env             # Environment config
├── package.json     # Project metadata & scripts
└── README.md
```

---

## 🚀 Future Improvements

- 🔌 **Backend Integration:** Connect to a live database for continuous updates.  
- 🧪 **Unit Testing:** Add tests for Svelte components and stores.  
- ⚡ **Performance:** Implement lazy loading for large charts and tables.  
- 📊 **Export Features:** Download metrics and user activity reports as CSV/PDF.

---

## 🙏 Acknowledgments

🙏 Huge thanks to the entire AsteelFlash team for the opportunity and support throughout my internship.  
Special thanks to my mentors for guiding me through the design and implementation of this project.

---

## 🔒 License

This project is for internal use at AsteelFlash and is not open source.  
All rights reserved by AsteelFlash.
