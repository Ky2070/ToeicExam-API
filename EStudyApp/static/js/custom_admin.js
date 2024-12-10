document.addEventListener('DOMContentLoaded', function () {
    const actionsSelect = document.querySelector('select[name="action"]');
    const submitBtn = document.querySelector('button[name="index"]');

    if (actionsSelect && submitBtn) {
        submitBtn.addEventListener('click', function (e) {
            const selectedAction = actionsSelect.value;
            if (selectedAction === 'mark_tests_published' || selectedAction === 'mark_tests_unpublished') {
                e.preventDefault();
                Swal.fire({
                    title: 'Bạn có chắc không?',
                    text: "Hành động này sẽ thay đổi trạng thái của các bài kiểm tra đã chọn.",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Xác nhận',
                    cancelButtonText: 'Hủy bỏ',
                }).then((result) => {
                    if (result.isConfirmed) {
                        document.querySelector('form').submit();
                    }
                });
            }
        });
    }
});

js = ('https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',)

document.addEventListener("DOMContentLoaded", function () {
    // Thu nhỏ cột trạng thái
    let statusColumn = document.querySelectorAll("td.column-colored_publish_status");
    statusColumn.forEach(cell => {
        cell.style.fontSize = "12px"; // Giảm kích thước chữ
    });

    // Tô màu các cột dựa trên nội dung
    let rows = document.querySelectorAll("tr");
    rows.forEach(row => {
        let statusCell = row.querySelector("td.column-colored_publish_status");
        if (statusCell && statusCell.textContent.includes("Publish")) {
            row.style.backgroundColor = "#e0f7e0"; // Màu xanh nhạt
        }
    });
});
