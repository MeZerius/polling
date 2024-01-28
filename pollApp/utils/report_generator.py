from datetime import datetime

from django.http import FileResponse
from django.utils.timezone import make_aware
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Line, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from django.utils import timezone

from io import BytesIO
from pollApp.models import Poll, Option


def add_legend(draw_obj, chart):
    legend = Legend()
    legend.alignment = 'right'
    legend.x = 10
    legend.y = 70
    legend.colorNamePairs = [
        (chart.slices[i].fillColor, (chart.labels[i][0:10] + '...') if len(chart.labels[i]) > 10 else chart.labels[i])
        for i in range(len(chart.data))]
    legend.fontSize = 14
    draw_obj.add(legend)


def pie_chart_with_legend(options):
    # Ensure all values are greater than zero
    data = [option.votes.count() if option.votes.count() > 0 else 0.1 for option in options]
    drawing = Drawing(400, 200)
    pie = Pie()
    pie.sideLabels = True
    pie.x = (letter[0] - pie.width) / 2.6
    pie.y = 20
    pie.width = 200
    pie.height = 200
    pie.data = data
    pie.labels = [option.text for option in options]
    pie.slices.strokeWidth = 0.5
    drawing.add(pie)
    add_legend(drawing, pie)
    return drawing


def generate_report(request, poll_id):
    poll = Poll.objects.get(id=poll_id)
    options = Option.objects.filter(poll=poll)
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0, leftMargin=0, rightMargin=0)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', alignment=1, fontSize=20, textColor=colors.black))
    story = []
    story.append(Paragraph(poll.title, styles['CustomTitle']))
    story.append(Spacer(1, 12))
    story.append(Spacer(1, 20))
    total_voter_count = sum(option.votes.count() for option in options)

    report_generated_time_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    naive_datetime = datetime.strptime(report_generated_time_str, '%Y-%m-%d %H:%M:%S')

    report_generated_time = make_aware(naive_datetime)

    if poll.start_time > report_generated_time:
        voting_result = "Upcoming"
    elif poll.is_invalid:
        voting_result = "Quorum isn't achieved"
    else:
        winner_option = max(options, key=lambda option: option.votes.count())
        winner_votes = winner_option.votes.count()
        other_votes = total_voter_count - winner_votes

        if poll.majority and winner_votes <= other_votes:
            voting_result = "There is no winner option for the majority."
        else:
            voting_result = f"The option '{winner_option.text}' won with {winner_votes} votes."

    if not poll.end_time and poll.active_time:
        poll.end_time = poll.start_time + poll.active_time

    status = 'Active' if poll.end_time and poll.end_time > report_generated_time else 'Closed'

    if poll.start_time > report_generated_time:
        status += ' (Upcoming Poll)'

    quorum_display = "disabled" if poll.quorum_type == "D" else f"{poll.quorum}%" if isinstance(poll.quorum,
                                                                                                str) and '%' in poll.quorum else str(
        poll.quorum)
    winner_option = max(options, key=lambda option: option.votes.count())
    majority_info = 'Yes' if poll.majority else 'No'

    data = [
        ['Status', status],
        ['Creator', str(poll.creator.username)],
        ['Majority', majority_info],
        ['Quorum', quorum_display],
        ['Total Voters', total_voter_count],
        ['Result of the voting', voting_result],

        ['Created At', str(poll.created_at)],
        ['Start Time', str(poll.start_time)],
        ['End Time', str(poll.end_time)],
        ['Report Generated Time', str(report_generated_time_str)],
    ]

    table = Table(data, colWidths=[letter[0] / 2.0] * 2)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 50))
    chart = pie_chart_with_legend(options)
    story.append(chart)
    pdf.build(story)
    buffer.seek(0)
    response = FileResponse(buffer, as_attachment=True, filename='poll_report.pdf')
    response['Content-Disposition'] = f'attachment; filename=poll_report.pdf'
    return response
