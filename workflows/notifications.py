from django.core.mail import send_mail


def notify_approver(request_obj):
    """Отправить email согласующему на текущем шаге."""
    current = request_obj.route.steps.filter(order=request_obj.current_step).first()
    if not current:
        return
    approver = current.approver
    if not approver.email:
        return

    send_mail(
        subject=f"[DocFlow] Требуется согласование: {request_obj.document.title}",
        message=(
            f"Здравствуйте, {approver.username}!\n\n"
            f"Документ: {request_obj.document.title}\n"
            f"Тип: {request_obj.document.get_doc_type_display()}\n"
            f"Шаг: {request_obj.current_step}\n\n"
            f"Откройте систему для согласования."
        ),
        from_email="noreply@docflow.local",
        recipient_list=[approver.email],
        fail_silently=True,
    )


def notify_owner_status_changed(request_obj):
    """Уведомить владельца о завершении согласования."""
    owner = request_obj.document.owner
    if not owner.email:
        return

    send_mail(
        subject=f"[DocFlow] Согласование завершено: {request_obj.document.title}",
        message=(
            f"Документ «{request_obj.document.title}» — "
            f"статус: {request_obj.get_status_display()}."
        ),
        from_email="noreply@docflow.local",
        recipient_list=[owner.email],
        fail_silently=True,
    )
