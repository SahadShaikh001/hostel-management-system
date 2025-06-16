// This file contains additional JavaScript functionality for the hostel management system

document.addEventListener("DOMContentLoaded", () => {
  // Preloader
  const preloader = document.getElementById("preloader")
  window.addEventListener("load", () => {
    preloader.style.opacity = "0"
    setTimeout(() => {
      preloader.style.display = "none"
    }, 500)
  })

  // Dropdown Menu Functionality
  const dropdowns = document.querySelectorAll(".dropdown")

  // Toggle dropdown on click
  dropdowns.forEach((dropdown) => {
    const toggle = dropdown.querySelector(".dropdown-toggle")

    toggle.addEventListener("click", (e) => {
      e.preventDefault()

      // Close all other dropdowns
      dropdowns.forEach((otherDropdown) => {
        if (otherDropdown !== dropdown && otherDropdown.classList.contains("active")) {
          otherDropdown.classList.remove("active")
        }
      })

      // Toggle current dropdown
      dropdown.classList.toggle("active")
    })
  })

  // Close dropdowns when clicking outside
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".dropdown")) {
      dropdowns.forEach((dropdown) => {
        dropdown.classList.remove("active")
      })
    }
  })

  // Mobile Menu Toggle
  const menuToggle = document.querySelector(".menu-toggle")
  const navMenu = document.querySelector(".nav-menu")

  if (menuToggle) {
    menuToggle.addEventListener("click", () => {
      menuToggle.classList.toggle("active")
      navMenu.classList.toggle("active")
      document.body.classList.toggle("menu-open")
    })

    // Close menu when clicking outside
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".nav-menu") && !e.target.closest(".menu-toggle") && navMenu.classList.contains("active")) {
        menuToggle.classList.remove("active")
        navMenu.classList.remove("active")
        document.body.classList.remove("menu-open")
      }
    })

    // Close menu when clicking on a link (except dropdown toggles)
    const navLinks = document.querySelectorAll(".nav-menu a:not(.dropdown-toggle)")
    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        menuToggle.classList.remove("active")
        navMenu.classList.remove("active")
        document.body.classList.remove("menu-open")
      })
    })
  }

  // Auto-hide alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert")
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.classList.remove("show")
      setTimeout(() => {
        alert.remove()
      }, 500)
    }, 5000)
  })

  // Scroll to top button
  const scrollTopBtn = document.getElementById("scroll-top")

  window.addEventListener("scroll", () => {
    if (window.pageYOffset > 300) {
      scrollTopBtn.classList.add("show")
    } else {
      scrollTopBtn.classList.remove("show")
    }
  })

  scrollTopBtn.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    })
  })

  // Initialize date inputs with today's date as minimum
  const dateInputs = document.querySelectorAll('input[type="date"]')
  const today = new Date().toISOString().split("T")[0]

  dateInputs.forEach((input) => {
    if (!input.min) {
      input.min = today
    }
  })

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href")
      if (targetId !== "#") {
        const target = document.querySelector(targetId)
        if (target) {
          e.preventDefault()
          target.scrollIntoView({
            behavior: "smooth",
            block: "start",
          })
        }
      }
    })
  })

  // Close modals when clicking outside
  const modals = document.querySelectorAll(".modal")
  modals.forEach((modal) => {
    modal.addEventListener("click", function (e) {
      if (e.target === this) {
        this.style.display = "none"
      }
    })
  })

  // FAQ accordion functionality
  const faqQuestions = document.querySelectorAll(".faq-question")
  if (faqQuestions.length > 0) {
    faqQuestions.forEach((question) => {
      question.addEventListener("click", function () {
        const answer = this.nextElementSibling

        // Toggle active class
        this.classList.toggle("active")

        // Toggle display of answer
        if (answer.style.maxHeight) {
          answer.style.maxHeight = null
        } else {
          answer.style.maxHeight = answer.scrollHeight + "px"
        }
      })
    })
  }

  // Add animation to elements when they come into view
  const animateOnScroll = () => {
    const elements = document.querySelectorAll(".section, .room-card, .team-member, .facility, .contact-card")

    elements.forEach((element) => {
      const elementPosition = element.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.2

      if (elementPosition < screenPosition) {
        element.classList.add("animate")
      }
    })
  }

  window.addEventListener("scroll", animateOnScroll)
  animateOnScroll() // Run once on page load

  // Handle logout form submission
  const logoutLink = document.querySelector(".logout-link")
  if (logoutLink) {
    logoutLink.addEventListener("click", (e) => {
      e.preventDefault()

      // Show confirmation dialog
      if (confirm("Are you sure you want to logout?")) {
        document.getElementById("logout-form").submit()
      }
    })
  }
})

// Function to generate a receipt for a stay record
function downloadReceipt(admissionCode) {
  fetch(`/api/receipt/${admissionCode}/`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok")
      }
      return response.blob()
    })
    .then((blob) => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `receipt_${admissionCode}.txt`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
    })
    .catch((error) => {
      console.error("Error downloading receipt:", error)
      alert("Could not download receipt. Please try again later.")
    })
}

// Function to show custom alert messages
function showAlert(message, type = "info") {
  const alertContainer = document.getElementById("alert-container")

  if (!alertContainer) return

  const alert = document.createElement("div")
  alert.className = `alert alert-${type}`

  alert.innerHTML = `
    <div class="alert-content">
      <i class="alert-icon fas ${type === "success" ? "fa-check-circle" : type === "error" ? "fa-exclamation-circle" : "fa-info-circle"}"></i>
      <span>${message}</span>
    </div>
    <button class="alert-close" onclick="this.parentElement.classList.remove('show');">&times;</button>
  `

  alertContainer.appendChild(alert)

  // Trigger reflow to enable animation
  alert.offsetWidth

  // Show the alert
  alert.classList.add("show")

  // Auto-hide after 5 seconds
  setTimeout(() => {
    alert.classList.remove("show")
    setTimeout(() => {
      alert.remove()
    }, 500)
  }, 5000)
}

