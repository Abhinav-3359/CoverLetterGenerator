import React, { useState } from 'react';
import axios from 'axios';

function CoverLetter() {
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
  const [resume, setResume] = useState(null);
  const [jobDesc, setJobDesc] = useState("");
  const [coverLetterText, setCoverLetterText] = useState("");
  const [loading, setLoading] = useState(false);
  const [showEditor, setShowEditor] = useState(false);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setCoverLetterText("");

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jobDesc);

    try {
      const response = await axios.post(`${BACKEND_URL}/generate-cover-letter-text`, formData);
      setCoverLetterText(response.data.cover_letter);
      setShowEditor(true);
    } catch (err) {
      alert("Error generating cover letter.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await axios.post(
        `${BACKEND_URL}/download-pdf`,
        { text: coverLetterText },
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'cover_letter.pdf');
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      alert("Error downloading PDF.");
      console.error(err);
    }
  };

  return (
    <div>
      <h2>Generate AI Cover Letter</h2>
      <form onSubmit={handleGenerate}>
        <div>
          <label>Upload Resume (PDF): </label>
          <input type="file" accept="application/pdf" onChange={(e) => setResume(e.target.files[0])} required />
        </div>
        <div>
          <label>Job Description:</label><br/>
          <textarea rows="10" cols="60" value={jobDesc} onChange={(e) => setJobDesc(e.target.value)} required />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate Cover Letter"}
        </button>
      </form>

      {showEditor && (
        <div style={{ marginTop: "20px" }}>
          <h3>Generated Cover Letter</h3>
          <textarea
            rows="15"
            cols="80"
            value={coverLetterText}
            onChange={(e) => setCoverLetterText(e.target.value)}
          />
          <br />
          <button onClick={handleDownload}>Download PDF</button>
        </div>
      )}
    </div>
  );
}

export default CoverLetter;
