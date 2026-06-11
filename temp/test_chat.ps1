$tests = @(
    @{ n=2; msg="Phòng 101 còn trống không?" },
    @{ n=3; msg="Hóa đơn tháng này của tôi bao nhiêu?" },
    @{ n=4; msg="Có bao nhiêu khách thuê đang ở?" },
    @{ n=5; msg="Nhắc tôi đóng tiền nhà cuối tháng" },
    @{ n=6; msg="Tôi là ai?" },
    @{ n=7; msg="Chủ trọ là ai?" }
)

foreach ($t in $tests) {
    $body = "{`"source`":`"web`",`"message`":`"$($t.msg)`",`"tenant_id`":1}"
    Write-Output "=== TEST $($t.n): $($t.msg) ==="
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30 -ErrorAction Stop
        $data = $r.Content | ConvertFrom-Json
        Write-Output "System: $($data.system_used) | Conf: $($data.confidence) | ${n}ms: $($data.latency_ms)"
        Write-Output "Answer: $($data.answer)"
        if ($data.tools_used.Count -gt 0) { Write-Output "Tools: $($data.tools_used -join ', ')" }
    } catch {
        Write-Output "ERROR: $_"
    }
    Write-Output "---"
}
