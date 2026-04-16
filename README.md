# Whisper Gate

**Whisper Gate** là một game escape room suy luận, nơi AI không chỉ là một NPC để đối thoại mà là cơ chế cốt lõi của gameplay.

Người chơi tỉnh dậy trong một cơ sở nghiên cứu ngầm đã bị phong tỏa sau một sự cố bí ẩn. Hệ thống điện chập chờn, dữ liệu bị chỉnh sửa, nhiều khu vực bị khóa, và gần như toàn bộ nhân sự đã biến mất. Thứ duy nhất còn hoạt động ổn định là một trí tuệ nhân tạo trung tâm mang tên **ORION**.

ORION không thân thiện, không thù địch, và cũng không tiết lộ sự thật một cách dễ dàng. Nó chỉ trả lời dựa trên những gì người chơi thực sự tìm thấy: tài liệu, vật phẩm, bản ghi và các dấu vết trong cơ sở. Muốn thoát khỏi nơi này, người chơi không chỉ cần mở khóa cánh cửa cuối cùng — **Whisper Gate** — mà còn phải học cách đặt câu hỏi đúng, kiểm tra độ tin cậy của dữ liệu, và tự suy luận giữa những thông tin mâu thuẫn.

## Core Idea

Whisper Gate kết hợp hai yếu tố chính:

- **Exploration**: khám phá phòng, tìm vật phẩm, mở khóa khu vực mới
- **AI Reasoning**: hỏi ORION về các bằng chứng đã tìm được để ghép nối sự thật

AI trong game không tự do “biết hết mọi thứ”. Nó chỉ phản hồi từ những context mà người chơi đã mở khóa. Vì vậy, tiến trình chơi không chỉ phụ thuộc vào việc đi đúng chỗ, mà còn phụ thuộc vào việc **hỏi đúng điều, đúng lúc**.

## Story Premise

Một dự án mang tên **Project Whisper** đã thất bại. Sau sự cố, cơ sở bị phong tỏa tự động, các bản ghi hệ thống trở nên đáng ngờ, và có dấu hiệu cho thấy một ai đó đã sửa đổi dữ liệu để che giấu sự thật.

Người chơi phải khám phá:

- Điều gì thực sự đã xảy ra trong cơ sở
- Ai đã thay đổi các bản ghi
- ORION đang che giấu điều gì
- Whisper Gate là lối thoát, hay chỉ là một phép thử cuối cùng

## How to Play

Người chơi nhập lệnh để tương tác với môi trường hoặc đặt câu hỏi trực tiếp cho ORION.

### 1. Action Commands

Dùng để khám phá, kiểm tra đồ vật, nhặt vật phẩm và mở khóa tiến trình.

Ví dụ:

- `look around`
- `inspect desk`
- `inspect terminal`
- `search locker`
- `open locker`
- `take keycard`
- `use keycard`
- `unlock door`

### 2. AI Questions

Dùng để hỏi ORION về những gì bạn đã tìm thấy.

Ví dụ:

- `Can the terminal logs be trusted?`
- `What happened in the generator room?`
- `Who altered the records?`
- `Should I trust ORION?`

Nếu input không khớp với action command, game sẽ xử lý nó như một câu hỏi gửi tới AI.

## Gameplay Loop

Vòng lặp chơi chính của game là:

**explore → collect evidence → question ORION → infer the truth → unlock new progress**

Một lượt chơi điển hình có thể như sau:

1. Quan sát môi trường
2. Khám phá một đồ vật hoặc khu vực
3. Tìm tài liệu hay vật phẩm mới
4. Hỏi ORION về ý nghĩa của những gì vừa tìm được
5. Dùng thông tin đó để mở khóa bước tiếp theo

## Available Commands

### Exploration
- `look around`
- `inspect <object>`
- `search <place>`
- `open <object>`
- `take <item>`
- `use <item>`
- `unlock <object>`

### Information
- `inventory`
- `documents`
- `state`
- `help`
