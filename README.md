
```
ansible-galaxy install -r requirements.yml
ansible-galaxy collection install community.general
ansible-playbook --ask-vault-pass -b -e @vm_vars.yml -e @vars/secure.yml -i vm_inventory -k -K playbook.yml
```