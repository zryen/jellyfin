import pytest
from os.path import dirname, join
from subprocess import check_output
from syncloudlib.integration.hosts import add_host_alias
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from integration.lib import login

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud/ui'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir, ui_mode):
    def module_teardown():
        device.activated()
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR, ui_mode), throw=False)
        device.run_ssh('cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR, ui_mode), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, ui_mode))
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, domain, device_host):
    add_host_alias(app, device_host, domain)


def test_login(selenium, device_user, device_password):
    login(selenium, device_user, device_password)


def test_admin(selenium):
    menu = selenium.find_by_css("span.material-icons.menu")
    selenium.wait_or_screenshot(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.material-icons.menu")))
    menu.click()
    button = selenium.find_by_css("span.navMenuOptionText")
    selenium.screenshot('menu')
    button.click()
    selenium.find_by_css("//span[text()='Scan All Libraries']")


def test_teardown(driver):
    driver.quit()
