import { makeAssistantToolUI } from '@assistant-ui/react'

type CreateInvoiceToolArgs = {
    customer_name: string;
    customer_email: string;
    amount: number;
    item: string;
    due_date?: string;
}

type InvoiceItem = {
    description: string;
    amount: number;
}

type InvoiceCustomer = {
    name: string;
    email: string;
}

type CreateInvoiceToolResult = {
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
}

const LoadingSpinner = () => (
    <div className="flex justify-center items-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
);

const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('nl-NL', { 
        style: 'currency', 
        currency: currency 
    }).format(amount);
};

const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('nl-NL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};

const InvoicePreview = ({ result }: { result: CreateInvoiceToolResult }) => {
    if (!result) return null;
    
    return (
        <div className="p-6 border rounded-lg shadow-md max-w-3xl mx-auto bg-white">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">INVOICE</h1>
                    <p className="text-gray-600 mt-1">#{result.invoice_number}</p>
                </div>
                <div className="text-right">
                    <div className="inline-block px-3 py-1 rounded-full bg-blue-100 text-blue-800 font-medium text-sm">
                        {result.status}
                    </div>
                </div>
            </div>
            
            <div className="grid grid-cols-2 gap-8 mb-8">
                <div>
                    <h2 className="text-sm font-semibold text-gray-600 uppercase mb-2">From</h2>
                    <p className="font-medium">Your Business Name</p>
                    <p className="text-gray-600">Your Address</p>
                    <p className="text-gray-600">Your City, Country</p>
                    <p className="text-gray-600">your.email@example.com</p>
                </div>
                <div>
                    <h2 className="text-sm font-semibold text-gray-600 uppercase mb-2">Bill To</h2>
                    <p className="font-medium">{result.customer.name}</p>
                    <p className="text-gray-600">{result.customer.email}</p>
                </div>
            </div>
            
            <div className="grid grid-cols-2 gap-8 mb-8">
                <div>
                    <h2 className="text-sm font-semibold text-gray-600 uppercase mb-2">Invoice Date</h2>
                    <p>{formatDate(result.invoice_date)}</p>
                </div>
                <div>
                    <h2 className="text-sm font-semibold text-gray-600 uppercase mb-2">Due Date</h2>
                    <p>{formatDate(result.due_date)}</p>
                </div>
            </div>
            
            <div className="mb-8">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-gray-200">
                            <th className="text-left py-3 px-2 text-sm font-semibold text-gray-600 uppercase">Description</th>
                            <th className="text-right py-3 px-2 text-sm font-semibold text-gray-600 uppercase">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {result.items.map((item, index) => (
                            <tr key={index} className="border-b border-gray-100">
                                <td className="py-4 px-2">{item.description}</td>
                                <td className="py-4 px-2 text-right">{formatCurrency(item.amount, result.currency)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            
            <div className="flex justify-end">
                <div className="w-1/2">
                    <div className="flex justify-between py-2">
                        <span className="font-medium">Subtotal:</span>
                        <span>{formatCurrency(result.subtotal, result.currency)}</span>
                    </div>
                    <div className="flex justify-between py-2">
                        <span className="font-medium">Tax ({(result.tax_rate * 100).toFixed(0)}%):</span>
                        <span>{formatCurrency(result.tax_amount, result.currency)}</span>
                    </div>
                    <div className="flex justify-between py-3 border-t border-gray-200 font-bold">
                        <span>Total:</span>
                        <span>{formatCurrency(result.total_amount, result.currency)}</span>
                    </div>
                </div>
            </div>
            
            <div className="mt-8 pt-8 border-t border-gray-200 text-center text-gray-600 text-sm">
                <p>Thank you for your business!</p>
                <p className="mt-2">Payment is due by {formatDate(result.due_date)}</p>
            </div>
        </div>
    );
};

export const CreateInvoiceToolUI = makeAssistantToolUI<CreateInvoiceToolArgs, CreateInvoiceToolResult>({
    toolName: "create_invoice",
    render: ({ result }) => {
        if (!result) return <LoadingSpinner />;
        return <InvoicePreview result={result} />;
    }
}); 