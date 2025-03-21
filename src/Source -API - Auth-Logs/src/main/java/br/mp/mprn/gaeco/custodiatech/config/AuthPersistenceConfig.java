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
        basePackages = "br.mp.mprn.gaeco.custodiatech.repository.auth",
        entityManagerFactoryRef = "autenticacaoEntityManager",
        transactionManagerRef = "autenticacaoTransactionManager"
)
public class AuthPersistenceConfig {

    @Autowired
    private Environment env;

    @Bean
    @Primary
    public LocalContainerEntityManagerFactoryBean autenticacaoEntityManager() {
        LocalContainerEntityManagerFactoryBean em
                = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(autenticacaoDataSource());
        em.setPackagesToScan(
                "br.mp.mprn.gaeco.custodiatech.model.auth");

        em.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        HashMap<String, Object> properties = new HashMap<>();
        properties.put("hibernate.hbm2ddl.auto",
                env.getProperty("hibernate.hbm2ddl.auto"));
        properties.put("hibernate.dialect",
                env.getProperty("hibernate.dialect"));
        em.setJpaPropertyMap(properties);

        return em;
    }

    @Primary
    @Bean
    public DataSource autenticacaoDataSource() {

        DriverManagerDataSource dataSource
                = new DriverManagerDataSource();
        dataSource.setDriverClassName(
                env.getProperty("spring.datasource.primary.driverClassName"));
        dataSource.setUrl(env.getProperty("spring.datasource.primary.url"));
        dataSource.setUsername(env.getProperty("spring.datasource.primary.username"));
        dataSource.setPassword(env.getProperty("spring.datasource.primary.password"));

        return dataSource;
    }

    @Primary
    @Bean
    public PlatformTransactionManager autenticacaoTransactionManager() {

        JpaTransactionManager transactionManager
                = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(
                autenticacaoEntityManager().getObject());
        return transactionManager;
    }
}
