const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// In-memory database (replace with MongoDB/MySQL later)
let cases = [];
let caseId = 1;

// Routes

// Submit a new case
app.post("/cases", (req, res) => {
    const { caseType, plaintiff, defendant, description } = req.body;

    if (!caseType || !plaintiff || !defendant || !description) {
        return res.status(400).json({ error: "All fields are required" });
    }

    const newCase = {
        id: caseId++,
        caseType,
        plaintiff,
        defendant,
        description,
        status: "Pending"
    };

    cases.push(newCase);
    res.json({ message: "Case submitted successfully", case: newCase });
});

// Get all cases
app.get("/cases", (req, res) => {
    res.json(cases);
});

// Get case details by ID
app.get("/cases/:id", (req, res) => {
    const caseId = parseInt(req.params.id);
    const foundCase = cases.find(c => c.id === caseId);

    if (!foundCase) {
        return res.status(404).json({ error: "Case not found" });
    }

    res.json(foundCase);
});

// Start server
app.listen(PORT, () => {
    console.log(`⚖️ Justice System backend running on http://localhost:${PORT}`);
});