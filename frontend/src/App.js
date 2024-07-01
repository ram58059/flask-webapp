import React, { useState, useEffect, useRef } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState('');
  const [data, setData] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalRows, setTotalRows] = useState(0);
  const [pageNumber, setPageNumber] = useState(1);
  const [selectedColumn, setSelectedColumn] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [totalPages, setTotalPages] = useState(0);
  const [sortColumn, setSortColumn] = useState('');
  const [sortDirection, setSortDirection] = useState('asc');

  const fileInputRef = useRef(null);
  const rowsPerPage = 10;

  useEffect(() => {
    if (searchQuery === '' && selectedColumn === '') {
      fetchData(filename, currentPage);
    } else {
      handleSearch();
    }
  }, [filename, currentPage, sortColumn, sortDirection]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setFilename(result.filename);
        setCurrentPage(0);
        fetchData(result.filename, 0);
      } else {
        console.error('Failed to upload file.');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const fetchData = async (filename, page) => {
    try {
      const response = await fetch(`http://localhost:5000/data?filename=${filename}&page=${page}&sortColumn=${sortColumn}&sortDirection=${sortDirection}`);
      if (response.ok) {
        const result = await response.json();
        setData(result.data); // Handle NaN values in data
        setHeaders(result.headers);
        setTotalRows(result.total_rows);
        setTotalPages(Math.ceil(result.total_rows / rowsPerPage));
        setPageNumber(page + 1);
      } else {
        console.error('Failed to fetch data.');
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleNextPage = () => {
    const nextPage = currentPage + 1;
    if (nextPage * rowsPerPage < totalRows) {
      setCurrentPage(nextPage);
    }
  };

  const handlePrevPage = () => {
    const prevPage = currentPage - 1;
    if (prevPage >= 0) {
      setCurrentPage(prevPage);
    }
  };

  const handleGoToPage = () => {
    if (pageNumber > 0 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber - 1);
    } else {
      console.error('Invalid page number');
    }
  };

  const handleClear = async () => {
    try {
      const response = await fetch('http://localhost:5000/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename }),
      });

      if (response.ok) {
        setFile(null);
        setFilename('');
        setData([]);
        setHeaders([]);
        setTotalRows(0);
        setTotalPages(0);
        setPageNumber(1);
        setSelectedColumn('');
        setSearchQuery('');
        if (fileInputRef.current) {
          fileInputRef.current.value = null; // Reset file input
        }
      } else {
        console.error('Failed to clear file.');
      }
    } catch (error) {
      console.error('Error clearing file:', error);
    }
  };

  const handleColumnChange = (e) => {
    setSelectedColumn(e.target.value);
  };

  const handleSearchInputChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleSearch = async () => {
    if (selectedColumn && searchQuery.trim() !== '') {
      try {
        const response = await fetch(`http://localhost:5000/filter?filename=${filename}&column=${selectedColumn}&query=${searchQuery}&page=${currentPage}`);
        if (response.ok) {
          const result = await response.json();
          setData(result.data); // Handle NaN values in data
          setHeaders(result.headers);
          setTotalRows(result.total_rows);
          setTotalPages(Math.ceil(result.total_rows / rowsPerPage));
          setPageNumber(currentPage + 1); // Update pageNumber based on currentPage
        } else {
          console.error('Failed to fetch filtered data.');
        }
      } catch (error) {
        console.error('Error fetching filtered data:', error);
      }
    } else {
      console.error('Please select a column and enter a search query.');
    }
  };

  const handleSort = (column) => {
    let direction = 'asc';
    if (sortColumn === column && sortDirection === 'asc') {
      direction = 'desc';
    }
    setSortColumn(column);
    setSortDirection(direction);
  };

  return (
    <div className="container mt-5">
      <h1 className="text-center">Upload Excel Sheet</h1>
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="form-group">
            <label htmlFor="excelFile">Choose Excel File:</label>
            <input
              type="file"
              className="form-control-file"
              id="excelFile"
              onChange={handleFileChange}
              ref={fileInputRef}
            />
          </div>
          <button className="btn btn-primary mr-2" onClick={handleUpload}>
            Upload
          </button>
          <button className="btn btn-warning" onClick={handleClear}>
            Clear
          </button>
        </div>
      </div>

      <div className="row mt-3">
        <div className="col-md-6">
          <div className="input-group">
            <select className="form-control" onChange={handleColumnChange} value={selectedColumn}>
              <option value="">Select Column</option>
              {headers.map((header, idx) => (
                <option key={idx} value={header}>{header}</option>
              ))}
            </select>
            <input
              type="text"
              className="form-control"
              placeholder="Search..."
              value={searchQuery}
              onChange={handleSearchInputChange}
            />
            <div className="input-group-append">
              <button className="btn btn-outline-secondary" type="button" onClick={handleSearch}>
                Search
              </button>
            </div>
          </div>
        </div>
      </div>

      {data.length > 0 ? (
        <div className="mt-5 table-container">
          <table className="table table-striped">
            <thead>
              <tr>
                {headers.map((header, idx) => (
                  <th key={idx}>
                    {header}
                    <button className="sort-button" onClick={() => handleSort(header)}>
                      <span className={`arrow ${sortColumn === header && sortDirection === 'asc' ? 'up' : 'down'}`}></span>
                    </button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={index}>
                  {headers.map((header, idx) => (
                    <td key={idx}>{row[header]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="d-flex justify-content-between align-items-center">
            <button
              className="btn btn-secondary"
              onClick={handlePrevPage}
              disabled={currentPage === 0}
            >
              Previous
            </button>
            <div className="d-flex align-items-center">
              <span>Page {pageNumber} of {totalPages}</span>
              <input
                type="number"
                className="ml-2 form-control"
                style={{ width: '80px' }}
                value={pageNumber}
                onChange={(e) => setPageNumber(Number(e.target.value))}
                min="1"
                max={totalPages}
              />
              <button className="btn btn-secondary ml-2" onClick={handleGoToPage}>
                Go
              </button>
            </div>
            <button
              className="btn btn-secondary"
              onClick={handleNextPage}
              disabled={(currentPage + 1) * rowsPerPage >= totalRows}
            >
              Next
            </button>
          </div>
        </div>
      ) : (
        <div className="mt-5 alert alert-warning">
          Please upload a file.
        </div>
      )}
    </div>
  );
}

export default App;