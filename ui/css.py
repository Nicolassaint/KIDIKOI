# css.py

TIMESTAMP_STYLE = """
<style>
    .transcript-container {
        margin: 20px 0;
        line-height: 1.6;
        font-size: 16px;
    }
    .timestamp-span {
        display: inline;
        cursor: pointer;
        padding: 2px 4px;
        margin: 0 2px;
        border-radius: 3px;
        background-color: #e9ecef;
        transition: background-color 0.2s;
    }
    .timestamp-span:hover {
        background-color: #dee2e6;
    }
    .timestamp-span:focus {
        outline: 3px solid #0d6efd;
        outline-offset: 2px;
    }
    .timestamp {
        font-weight: bold;
        color: #0d6efd;
        margin-right: 4px;
        font-size: 14px;
    }
</style>
"""
