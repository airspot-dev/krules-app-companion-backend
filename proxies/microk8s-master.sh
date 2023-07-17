gcloud compute ssh \
 --project airspot-krules-companion-dev --zone europe-west4-a \
 ubuntu@microk8s-master --ssh-flag="-L 16443:localhost:16443"