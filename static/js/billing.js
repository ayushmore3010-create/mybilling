// Interactive Dynamic Billing Calculation Engine for MyBillingSystem

document.addEventListener('DOMContentLoaded', function () {
    const itemsTableBody = document.getElementById('billing-items-body');
    const addRowBtn = document.getElementById('add-product-row-btn');

    if (!itemsTableBody) return;

    // Attach listeners to initial rows
    attachRowListenersAll();
    calculateTotals();

    if (addRowBtn) {
        addRowBtn.addEventListener('click', function () {
            addNewRow();
        });
    }

    function addNewRow() {
        const rowId = 'row-' + Date.now();
        const tr = document.createElement('tr');
        tr.className = 'item-row border-b border-slate-100 hover:bg-slate-50/50 transition';
        tr.id = rowId;

        tr.innerHTML = `
            <td class="p-3">
                <input type="text" name="product_name[]" class="product-name-input w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm font-medium" placeholder="Type product name or select..." required autocomplete="off">
                <input type="hidden" name="product_id[]" class="product-id-input" value="">
            </td>
            <td class="p-3 w-28">
                <input type="number" step="any" name="quantity[]" value="1" min="0.01" class="qty-input w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-center font-semibold" required>
            </td>
            <td class="p-3 w-28">
                <select name="unit[]" class="unit-select w-full px-2 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-xs font-medium bg-white">
                    <option value="Piece">Piece</option>
                    <option value="Kg">Kg</option>
                    <option value="Gram">Gram</option>
                    <option value="Liter">Liter</option>
                    <option value="Meter">Meter</option>
                    <option value="Box">Box</option>
                    <option value="Packet">Packet</option>
                </select>
            </td>
            <td class="p-3 w-32">
                <div class="relative">
                    <span class="absolute left-2.5 top-2.5 text-slate-400 text-xs font-semibold">₹</span>
                    <input type="number" step="any" name="rate[]" value="0.00" min="0" class="rate-input w-full pl-6 pr-2 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm text-right font-semibold" required>
                </div>
            </td>
            <td class="p-3 w-28">
                <div class="relative">
                    <input type="number" step="any" name="discount[]" value="0" min="0" max="100" class="discount-input w-full pr-6 pl-2 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm text-right font-medium">
                    <span class="absolute right-2.5 top-2.5 text-slate-400 text-xs font-semibold">%</span>
                </div>
            </td>
            <td class="p-3 w-28">
                <select name="gst_rate[]" class="gst-select w-full px-2 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-xs font-semibold bg-white">
                    <option value="0">0%</option>
                    <option value="5">5%</option>
                    <option value="12">12%</option>
                    <option value="18" selected>18%</option>
                    <option value="28">28%</option>
                </select>
            </td>
            <td class="p-3 w-36 text-right font-bold text-slate-800 text-sm">
                <span class="line-total-display">₹0.00</span>
            </td>
            <td class="p-3 w-12 text-center">
                <button type="button" class="remove-row-btn text-rose-500 hover:text-rose-700 hover:bg-rose-50 p-1.5 rounded-lg transition" title="Remove Item">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
            </td>
        `;

        itemsTableBody.appendChild(tr);
        attachRowListeners(tr);
        calculateTotals();
    }

    function attachRowListenersAll() {
        const rows = itemsTableBody.querySelectorAll('.item-row');
        rows.forEach(attachRowListeners);
    }

    function attachRowListeners(row) {
        const qtyInput = row.querySelector('.qty-input');
        const rateInput = row.querySelector('.rate-input');
        const discountInput = row.querySelector('.discount-input');
        const gstSelect = row.querySelector('.gst-select');
        const removeBtn = row.querySelector('.remove-row-btn');
        const pNameInput = row.querySelector('.product-name-input');

        [qtyInput, rateInput, discountInput, gstSelect, pNameInput].forEach(elem => {
            if (elem) {
                elem.addEventListener('input', calculateTotals);
                elem.addEventListener('change', calculateTotals);
            }
        });

        if (removeBtn) {
            removeBtn.addEventListener('click', function () {
                const totalRows = itemsTableBody.querySelectorAll('.item-row').length;
                if (totalRows > 1) {
                    row.remove();
                    calculateTotals();
                } else {
                    alert("A bill must have at least one product row.");
                }
            });
        }
    }

    function calculateTotals() {
        const rows = itemsTableBody.querySelectorAll('.item-row');
        let grossSubtotal = 0;
        let totalDiscountVal = 0;
        let totalTaxableVal = 0;
        let totalTaxVal = 0;

        rows.forEach(row => {
            const qty = parseFloat(row.querySelector('.qty-input')?.value || 0);
            const rate = parseFloat(row.querySelector('.rate-input')?.value || 0);
            const discPercent = parseFloat(row.querySelector('.discount-input')?.value || 0);
            const gstPercent = parseFloat(row.querySelector('.gst-select')?.value || 0);

            const lineGross = qty * rate;
            const lineDisc = (lineGross * discPercent) / 100.0;
            const lineTaxable = Math.max(0, lineGross - lineDisc);
            const lineTax = (lineTaxable * gstPercent) / 100.0;
            const lineTotal = lineTaxable + lineTax;

            const lineTotalDisplay = row.querySelector('.line-total-display');
            if (lineTotalDisplay) {
                lineTotalDisplay.textContent = '₹' + lineTotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            }

            grossSubtotal += lineGross;
            totalDiscountVal += lineDisc;
            totalTaxableVal += lineTaxable;
            totalTaxVal += lineTax;
        });

        const grandTotal = totalTaxableVal + totalTaxVal;
        const cgstVal = totalTaxVal / 2.0;
        const sgstVal = totalTaxVal / 2.0;

        // Update Summary Card elements
        updateText('subtotal-display', grossSubtotal);
        updateText('discount-display', totalDiscountVal);
        updateText('taxable-display', totalTaxableVal);
        updateText('cgst-display', cgstVal);
        updateText('sgst-display', sgstVal);
        updateText('totaltax-display', totalTaxVal);
        updateText('grandtotal-display', grandTotal);
    }

    function updateText(elementId, val) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = '₹' + val.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
    }
});
