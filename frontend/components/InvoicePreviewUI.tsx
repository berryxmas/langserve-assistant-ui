// frontend/components/InvoicePreviewUI.tsx
import React, { useState } from 'react';
import { makeAssistantToolUI } from '@assistant-ui/react';
import { Modal } from './Modal';

type CreateInvoiceToolArgs = {
    customer_name: string;
    customer_email: string;
    amount: number;
    item: string;
    due_date?: string;
    tax_rate?: number;
}

type InvoiceItem = {
    description: string;
    amount: number;
}

type InvoiceCustomer = {
    name: string;
    email: string;
}

type InvoicePDF = {
    filename: string;
    filepath: string;
    size: number;
    pages: number;
    url: string;
}

type InvoiceData = {
    invoice_number: string;
    invoice_date: string;
    due_date: string;
    customer: InvoiceCustomer;
    items: InvoiceItem[];
    subtotal: number;
    tax_rate: number;
    tax_amount: number;
    total_amount: number;
    currency: string;
    status: string;
    pdf: InvoicePDF;
}

// The result is now directly the invoice data
type CreateInvoiceToolResult = InvoiceData;

const LoadingSpinner = () => (
    <div className="flex justify-center items-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
);

const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    const kb = bytes / 1024;
    if (kb < 1024) return Math.round(kb) + ' KB';
    const mb = kb / 1024;
    return mb.toFixed(1) + ' MB';
};

const InvoicePreview = ({ result }: { result: CreateInvoiceToolResult }) => {
    const [modalOpen, setModalOpen] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);
    
    if (!result || !result.pdf) {
        return <div className="text-red-500 p-4">Error: Invalid invoice data</div>;
    }
    
    const { pdf } = result;
    const pdfUrl = `http://localhost:8000${pdf.url}`;
    
    const handleViewPDF = () => {
        setModalOpen(true);
        setMenuOpen(false);
    };
    
    const handleDownload = () => {
        // Create a link element and trigger download
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = pdf.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        setMenuOpen(false);
    };
    
    const handleShare = async () => {
        if (navigator.share) {
            try {
                await navigator.share({
                    title: `Invoice ${result.invoice_number}`,
                    text: `Invoice for ${result.customer.name}`,
                    url: pdfUrl,
                });
            } catch (error) {
                console.error('Error sharing:', error);
            }
        } else {
            // Fallback for browsers that don't support navigator.share
            handleDownload();
        }
        setMenuOpen(false);
    };
    
    return (
        <div className="rounded-lg overflow-hidden bg-white my-4 shadow-md max-w-sm">
            {/* Upper half - PDF preview */}
            <div 
                className="h-40 bg-gray-100 flex justify-center items-center cursor-pointer relative overflow-hidden"
                onClick={handleViewPDF}
            >
                {/* Use an object tag for the preview */}
                <object 
                    data={pdfUrl}
                    type="application/pdf"
                    className="w-full h-full absolute inset-0 scale-150 origin-top"
                >
                    <div className="flex items-center justify-center h-full">
                        <p className="text-gray-500">PDF preview not available</p>
                    </div>
                </object>
                <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-10 transition-all z-10"></div>
            </div>
            
            {/* Lower half - File info and options */}
            <div className="flex p-3 items-center border-t border-gray-200">
                <div className="mr-3">
                    <div className="w-10 h-10 bg-red-500 rounded flex justify-center items-center">
                        <span className="text-white font-bold text-xs">PDF</span>
                    </div>
                </div>
                
                <div className="flex-1">
                    <p className="text-sm font-medium">{pdf.filename}</p>
                    <p className="text-xs text-gray-500">
                        {pdf.pages} {pdf.pages === 1 ? 'page' : 'pages'} • {formatFileSize(pdf.size)} • pdf
                    </p>
                </div>
                
                <div className="relative">
                    <button 
                        className="p-1 rounded-full hover:bg-gray-100"
                        onClick={() => setMenuOpen(!menuOpen)}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                        </svg>
                    </button>
                    
                    {menuOpen && (
                        <div className="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg z-10 py-1">
                            <button 
                                className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                                onClick={handleViewPDF}
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                                </svg>
                                View
                            </button>
                            
                            <button 
                                className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                                onClick={handleDownload}
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                                </svg>
                                Download
                            </button>
                            
                            <button 
                                className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                                onClick={handleShare}
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                                    <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
                                </svg>
                                Share
                            </button>
                        </div>
                    )}
                </div>
            </div>
            
            {/* PDF Viewer Modal */}
            <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)}>
                <div className="bg-white rounded-lg overflow-hidden max-w-4xl w-full max-h-[90vh]">
                    <div className="flex justify-between items-center p-4 border-b">
                        <h3 className="text-lg font-medium">Invoice {result.invoice_number}</h3>
                        <div className="flex space-x-2">
                            <button 
                                onClick={handleShare}
                                className="p-2 rounded-full hover:bg-gray-100"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
                                </svg>
                            </button>
                            <button 
                                onClick={() => setModalOpen(false)}
                                className="p-2 rounded-full hover:bg-gray-100"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    <div className="p-4 overflow-auto" style={{ height: 'calc(90vh - 70px)' }}>
                        {/* Use an embed tag for the full PDF view */}
                        <embed 
                            src={pdfUrl}
                            type="application/pdf"
                            className="w-full"
                            style={{ height: 'calc(90vh - 100px)' }}
                        />
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export const InvoicePreviewUI = makeAssistantToolUI<CreateInvoiceToolArgs, CreateInvoiceToolResult>({
    toolName: "create_invoice",
    render: ({ result }) => {
        if (!result) return <LoadingSpinner />;
        
        try {
            return <InvoicePreview result={result} />;
        } catch (error) {
            console.error("Error rendering invoice preview:", error);
            return <div className="text-red-500 p-4">Error rendering invoice preview</div>;
        }
    }
});