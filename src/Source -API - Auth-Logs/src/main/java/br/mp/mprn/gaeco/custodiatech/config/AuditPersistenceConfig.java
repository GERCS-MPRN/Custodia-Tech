package br.mp.mprn.gaeco.custodiatech.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.core.env.Environment;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;
import org.springframework.transaction.PlatformTransactionManager;

import javax.sql.DataSource;
import java.util.HashMap;

@Configuration
@EnableJpaRepositories(
        basePackages = "br.mp.mprn.gaeco.custodiatech.repository.auditoria",
        entityManagerFactoryRef = "auditoriaEntityManager",
        transactionManagerRef = "auditoriaTransactionManager"
)
public class AuditPersistenceConfig {

    @Autowired
    private Environment env;

    @Bean
    public LocalContainerEntityManagerFactoryBean auditoriaEntityManager() {
        LocalContainerEntityManagerFactoryBean em
                = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(auditoriaDataSource());
        em.setPackagesToScan(
                "br.mp.mprn.gaeco.custodiatech.model.auditoria");

        em.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        HashMap<String, Object> properties = new HashMap<>();
        properties.put("hibernate.hbm2ddl.auto",
                env.getProperty("hibernate.hbm2ddl.auto"));
        properties.put("hibernate.dialect",
                env.getProperty("hibernate.dialect"));
        em.setJpaPropertyMap(properties);

        return em;
    }

    @Bean
    public DataSource auditoriaDataSource() {

        DriverManagerDataSource dataSource
                = new DriverManagerDataSource();
        dataSource.setDriverClassName(
                env.getProperty("spring.datasource.secondary.driverClassName"));
        dataSource.setUrl(env.getProperty("spring.datasource.secondary.url"));
        dataSource.setUsername(env.getProperty("spring.datasource.secondary.username"));
        dataSource.setPassword(env.getProperty("spring.datasource.secondary.password"));

        return dataSource;
    }

    @Primary
    @Bean
    public PlatformTransactionManager auditoriaTransactionManager() {

        JpaTransactionManager transactionManager
                = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(
                auditoriaEntityManager().getObject());
        return transactionManager;
    }
}
