# 🎨 NutriAI Theme Customization Guide

## Quick Start: Change Colors in 2 Minutes

**All theme colors are controlled from ONE file: `src/index.css`**

### Step 1: Open the theme file
```bash
# Open in your editor
src/index.css
```

### Step 2: Find the `:root` section (around line 19)
```css
:root {
  --primary: 142 76% 36%;           /* Main brand color */
  --accent: 24 100% 50%;             /* Highlight color */
  /* ... other colors */
}
```

### Step 3: Change the values
Replace the numbers with your desired colors (HSL format)

### Step 4: Save and reload
The entire app updates instantly!

---

## 🌈 Understanding HSL Color Format

Colors use HSL format: `Hue Saturation% Lightness%`

```
--primary: 142 76% 36%;
           ↑   ↑   ↑
           |   |   └─ Lightness (0-100%)
           |   └───── Saturation (0-100%)
           └───────── Hue (0-360)
```

### HSL Examples
```css
/* Greens */
142 76% 36%  →  #22c55e (Vibrant green)
142 71% 45%  →  #10b981 (Emerald)
142 69% 58%  →  #4ade80 (Light green)

/* Blues */
221 83% 53%  →  #3b82f6 (Bright blue)
217 91% 60%  →  #60a5fa (Sky blue)
211 98% 63%  →  #70b7f5 (Light blue)

/* Oranges/Corals */
24 100% 50%  →  #ff8000 (Energy orange)
12 76% 61%   →  #f87171 (Coral)
38 92% 50%   →  #fb923c (Amber)

/* Purples */
262 83% 58%  →  #a855f7 (Purple)
270 95% 75%  →  #c084fc (Light purple)
```

---

## 🎯 Pre-Made Theme Presets

### Option 1: Fresh & Healthy (Default - Active)
**Perfect for nutrition/health apps**
```css
:root {
  --primary: 142 76% 36%;           /* #22c55e - Vibrant green */
  --accent: 24 100% 50%;             /* #ff8000 - Energy orange */
}
```
✅ Already active!

### Option 2: Professional Medical
**Trustworthy and professional**
```css
:root {
  --primary: 221 83% 53%;           /* #3b82f6 - Trust blue */
  --accent: 142 76% 36%;             /* #22c55e - Health green */
}
```

### Option 3: Warm & Inviting
**Friendly and approachable**
```css
:root {
  --primary: 12 76% 61%;            /* #f87171 - Warm coral */
  --accent: 38 92% 50%;              /* #fb923c - Friendly amber */
}
```

---

## 📋 Complete Color Variable Reference

### Primary Brand Colors
```css
--primary: 142 76% 36%;              /* Main buttons, links, CTAs */
--primary-foreground: 0 0% 100%;     /* Text on primary elements */
```
**Use for:** Buttons, active states, primary actions

### Accent Colors
```css
--accent: 24 100% 50%;               /* Highlights, hover states */
--accent-foreground: 0 0% 100%;      /* Text on accent elements */
```
**Use for:** Badges, highlights, secondary CTAs

### Background & Surfaces
```css
--background: 0 0% 100%;             /* Page background (white) */
--foreground: 240 10% 3.9%;         /* Main text color (dark) */
--card: 0 0% 100%;                   /* Card backgrounds */
--card-foreground: 240 10% 3.9%;    /* Text on cards */
```
**Use for:** Page layouts, cards, panels

### UI Elements
```css
--border: 240 5.9% 90%;              /* Borders and dividers */
--input: 240 5.9% 90%;               /* Input field borders */
--ring: 142 76% 36%;                 /* Focus rings (matches primary) */
```
**Use for:** Input fields, borders, separators

### Status Colors
```css
--destructive: 0 84.2% 60.2%;       /* Errors, delete actions (red) */
--success: 142 76% 36%;              /* Success messages (green) */
--warning: 38 92% 50%;               /* Warnings (amber) */
```
**Use for:** Alerts, notifications, status indicators

### Secondary/Muted
```css
--secondary: 240 4.8% 95.9%;        /* Less prominent elements */
--muted: 240 4.8% 95.9%;             /* Disabled/subtle backgrounds */
--muted-foreground: 240 3.8% 46.1%; /* Subtle text */
```
**Use for:** Disabled states, placeholders, subtle UI

---

## 🛠️ Tools for Finding Colors

### Option 1: shadcn/ui Theme Generator (Recommended)
1. Visit: https://ui.shadcn.com/themes
2. Pick colors visually
3. Copy the HSL values
4. Paste into `src/index.css`

### Option 2: HSL Color Picker
- https://hslpicker.com/
- Adjust sliders to find your color
- Copy HSL values (without `hsl()` wrapper)

### Option 3: Convert from HEX
If you have a HEX color (#22c55e):
1. Use: https://www.rapidtables.com/convert/color/hex-to-hsl.html
2. Enter your HEX
3. Get HSL values
4. Use format: `H S% L%` (example: `142 76% 36%`)

---

## 🌓 Dark Mode

Dark mode colors are automatically configured in `src/index.css`:

```css
.dark {
  --primary: 142 76% 36%;           /* Same green works in dark! */
  --background: 240 10% 3.9%;       /* Dark background */
  --foreground: 0 0% 98%;           /* Light text */
  /* ... other dark mode colors */
}
```

**To customize dark mode:**
1. Find the `.dark` section in `src/index.css`
2. Adjust colors as needed
3. Usually only need to change background/foreground

---

## 💡 Best Practices

### ✅ Do's
- **Keep high contrast** between text and backgrounds
- **Test accessibility** - use tools like https://webaim.org/resources/contrastchecker/
- **Use semantic colors** - primary for main actions, destructive for delete
- **Test in both light and dark mode**

### ❌ Don'ts
- Don't use very low saturation (<30%) for primary colors
- Don't use very high lightness (>80%) for primary colors
- Don't forget to update both light and dark modes
- Don't use too many different colors (stick to your palette)

---

## 🎨 Example: Changing to Blue Theme

### Before (Green):
```css
:root {
  --primary: 142 76% 36%;           /* Green */
  --accent: 24 100% 50%;             /* Orange */
}
```

### After (Blue):
```css
:root {
  --primary: 221 83% 53%;           /* Blue */
  --accent: 217 91% 60%;             /* Light blue */
}
```

Save the file, and every button, link, and primary element turns blue instantly!

---

## 🔍 Where Colors Are Used

| Component | Primary | Accent | Destructive | Border |
|-----------|---------|--------|-------------|--------|
| Buttons | ✅ | ✅ | ✅ | - |
| Links | ✅ | - | - | - |
| Input Focus | - | - | - | ✅ (ring) |
| Badges | - | ✅ | - | ✅ |
| Cards | - | - | - | ✅ |
| Alerts | - | - | ✅ | - |
| Recipe Cards | ✅ | ✅ | - | ✅ |
| Navigation | ✅ | - | - | - |

---

## 🚀 Quick Theme Recipes

### Fitness App (Energetic)
```css
--primary: 14 100% 57%;   /* Bright red-orange */
--accent: 45 93% 58%;     /* Yellow */
```

### Vegan/Plant-Based (Natural)
```css
--primary: 142 76% 36%;   /* Green (default) */
--accent: 84 81% 44%;     /* Lime */
```

### Medical/Clinical (Professional)
```css
--primary: 200 98% 39%;   /* Clinical blue */
--accent: 198 93% 60%;    /* Light blue */
```

### Wellness (Calming)
```css
--primary: 262 83% 58%;   /* Purple */
--accent: 270 95% 75%;    /* Light purple */
```

---

## 📝 Summary

1. **Open**: `src/index.css`
2. **Find**: `:root` section
3. **Edit**: Color values (`--primary`, `--accent`, etc.)
4. **Save**: Changes apply immediately
5. **Test**: Check both light and dark modes

**That's it! Your entire app theme updates from one file.**

---

## 🆘 Need Help?

- Colors not showing? Make sure you're editing `src/index.css`
- Contrast issues? Use https://webaim.org/resources/contrastchecker/
- Want more colors? Use https://ui.shadcn.com/themes
- Dark mode looks wrong? Check the `.dark` section in `src/index.css`

---

**🎉 Happy theming!**
