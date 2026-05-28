<?php
/**
 * Plugin Name: Service CRM
 * Description: CRM система сервисного центра.
 * Version: 0.1
 */

if (!defined('ABSPATH')) {
    exit;
}

function service_crm_shortcode() {
    ob_start();
    ?>

    <div class="service-crm-wrap">
        <h2>Service CRM</h2>

        <div class="crm-orders">
            <div class="crm-order-card">
                <h3>Заказ #1001</h3>
                <p>Клиент: Иван</p>
                <p>Статус: Диагностика</p>
            </div>
        </div>
    </div>

    <?php
    return ob_get_clean();
}

add_shortcode('service_crm', 'service_crm_shortcode');
